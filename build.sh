git clone git@github.com:danyal-s/perspective-backend.git backend
git clone git@github.com:danyal-s/perspective-frontend.git frontend
if [[ ! -f ".env" ]]; then
    cp .env-sample .env
fi
