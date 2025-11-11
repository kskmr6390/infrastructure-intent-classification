#!/bin/bash
# Automated Heroku Deployment Script for Intent Classification System
# This script checks prerequisites and deploys your app to Heroku

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# Check if Heroku CLI is installed
check_heroku_cli() {
    if ! command -v heroku &> /dev/null; then
        print_error "Heroku CLI is not installed"
        echo ""
        echo "Install it with:"
        echo "  Mac: brew tap heroku/brew && brew install heroku"
        echo "  Other: https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    print_success "Heroku CLI is installed"
}

# Check if logged into Heroku
check_heroku_login() {
    if ! heroku auth:whoami &> /dev/null; then
        print_error "Not logged into Heroku"
        echo ""
        echo "Please login with: heroku login"
        exit 1
    fi
    local user=$(heroku auth:whoami 2>/dev/null)
    print_success "Logged into Heroku as: $user"
}

# Check if models are trained
check_models() {
    if [ ! -d "ml/model/saved_models" ] || [ -z "$(ls -A ml/model/saved_models 2>/dev/null)" ]; then
        print_error "No trained models found in ml/model/saved_models/"
        echo ""
        echo "Train a model first:"
        echo "  source venv/bin/activate"
        echo "  python -m ml.traditional_ml.train"
        exit 1
    fi
    
    local model_count=$(ls ml/model/saved_models/*.pkl 2>/dev/null | wc -l)
    if [ "$model_count" -gt 0 ]; then
        print_success "Found $model_count model file(s)"
        
        # Check if models are tracked by git
        if git ls-files --error-unmatch ml/model/saved_models/*.pkl &> /dev/null; then
            print_success "Models are tracked by Git"
        else
            print_warning "Models are NOT tracked by Git"
            echo ""
            echo "Models must be committed to Git for Heroku deployment."
            echo ""
            echo "Options:"
            echo "1. Edit .gitignore and comment out: ml/model/saved_models/*.pkl"
            echo "2. Force add: git add -f ml/model/saved_models/*.pkl"
            echo ""
            read -p "Do you want to force add models now? (y/n) " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                git add -f ml/model/saved_models/*.pkl
                print_success "Models added to Git"
            else
                print_error "Cannot deploy without models in Git"
                exit 1
            fi
        fi
    else
        print_error "No .pkl model files found"
        exit 1
    fi
}

# Check git status
check_git_status() {
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "You have uncommitted changes"
        echo ""
        git status --short
        echo ""
        read -p "Do you want to commit these changes? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "Enter commit message: " commit_msg
            git add .
            git commit -m "$commit_msg"
            print_success "Changes committed"
        else
            print_info "Continuing with uncommitted changes (won't be deployed)"
        fi
    else
        print_success "Git working directory is clean"
    fi
}

# Check if Heroku app exists
check_heroku_app() {
    if git remote | grep -q "^heroku$"; then
        local app_name=$(heroku apps:info -r heroku 2>/dev/null | grep "^===" | cut -d' ' -f2)
        if [ -n "$app_name" ]; then
            print_success "Heroku app exists: $app_name"
            HEROKU_APP_NAME="$app_name"
            return 0
        fi
    fi
    
    print_warning "No Heroku app found"
    echo ""
    read -p "Do you want to create a new Heroku app? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter app name (leave empty for auto-generated): " app_name
        if [ -z "$app_name" ]; then
            heroku create
        else
            heroku create "$app_name"
        fi
        HEROKU_APP_NAME=$(heroku apps:info 2>/dev/null | grep "^===" | cut -d' ' -f2)
        print_success "Created Heroku app: $HEROKU_APP_NAME"
    else
        print_error "Cannot deploy without a Heroku app"
        exit 1
    fi
}

# Estimate slug size
estimate_slug_size() {
    print_info "Estimating deployment size..."
    
    local total_size=$(du -sh . 2>/dev/null | cut -f1)
    print_info "Total directory size: $total_size"
    
    local model_size=$(du -sh ml/model/saved_models 2>/dev/null | cut -f1)
    print_info "Model files size: $model_size"
    
    # Warning if likely to be too large
    local size_bytes=$(du -s . 2>/dev/null | cut -f1)
    local max_size=$((500 * 1024))  # 500MB in KB
    
    if [ "$size_bytes" -gt "$max_size" ]; then
        print_warning "Directory size may exceed Heroku's 500MB slug limit"
        echo "Consider using a smaller model or adding files to .slugignore"
    fi
}

# Configure environment variables
configure_env_vars() {
    print_info "Configuring environment variables..."
    
    # Set DEBUG to false for production
    heroku config:set DEBUG=false
    print_success "Set DEBUG=false"
    
    # Ask about LangSmith
    read -p "Do you want to enable LangSmith observability? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your LangSmith API key: " langsmith_key
        if [ -n "$langsmith_key" ]; then
            heroku config:set LANGCHAIN_TRACING_V2=true
            heroku config:set LANGCHAIN_API_KEY="$langsmith_key"
            heroku config:set LANGCHAIN_PROJECT=intent-classification
            print_success "LangSmith configured"
        fi
    fi
}

# Deploy to Heroku
deploy_to_heroku() {
    print_info "Deploying to Heroku..."
    echo ""
    
    # Get current branch
    local branch=$(git rev-parse --abbrev-ref HEAD)
    
    if [ "$branch" = "main" ] || [ "$branch" = "master" ]; then
        git push heroku "$branch"
    else
        print_warning "You're on branch '$branch' (not main/master)"
        read -p "Push $branch to Heroku main? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git push heroku "$branch:main"
        else
            print_error "Deployment cancelled"
            exit 1
        fi
    fi
    
    print_success "Deployment complete!"
}

# Scale dyno
scale_dyno() {
    print_info "Scaling web dyno..."
    heroku ps:scale web=1
    print_success "Web dyno scaled to 1"
}

# Show deployment info
show_deployment_info() {
    print_header "Deployment Complete!"
    
    local app_url=$(heroku apps:info -r heroku 2>/dev/null | grep "Web URL" | awk '{print $3}')
    
    echo -e "${GREEN}Your app is now live!${NC}"
    echo ""
    echo "App URL: $app_url"
    echo "API Docs: ${app_url}docs"
    echo ""
    echo "Useful commands:"
    echo "  heroku open                 # Open app in browser"
    echo "  heroku logs --tail          # View logs"
    echo "  heroku ps                   # Check dyno status"
    echo "  heroku config               # View environment variables"
    echo ""
    
    read -p "Do you want to open the app in your browser? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        heroku open
    fi
}

# Main deployment flow
main() {
    print_header "Heroku Deployment - Intent Classification System"
    
    print_header "Step 1: Checking Prerequisites"
    check_heroku_cli
    check_heroku_login
    check_models
    check_git_status
    
    print_header "Step 2: Heroku App Setup"
    check_heroku_app
    estimate_slug_size
    
    print_header "Step 3: Configuration"
    read -p "Do you want to configure environment variables? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        configure_env_vars
    fi
    
    print_header "Step 4: Deployment"
    echo "Ready to deploy to Heroku"
    echo ""
    read -p "Continue with deployment? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Deployment cancelled"
        exit 1
    fi
    
    deploy_to_heroku
    scale_dyno
    
    show_deployment_info
    
    print_success "All done! 🚀"
}

# Run main function
main

