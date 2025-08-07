# FastAPI + SvelteKit Boilerplate

A full-stack authentication boilerplate with FastAPI backend and SvelteKit frontend.

## Quick Setup

### Backend Setup
1. Create && activate your venv: `python3 -m venv venv && source venv/bin/activate`
2. open or `cd` into backend. With the venv active, install dependencies into the venv: `pip install -r requirements.txt`
3. On render.com set up new PostgreSQL database and update `DATABASE_URL`
4. Get Resend API key from [resend.com](https://resend.com) and add to `RESEND_API_KEY`
5. Run: `uvicorn backend.main:app --reload --port 8000`

### Frontend Setup
1. in /frontend rename `env.example` to `.env`
2. Install dependencies: `npm install`
3. Run: `npm run dev`

## Database Setup
- Create PostgreSQL database
- Update `DATABASE_URL` in backend `.env` file
- Tables will be created automatically on first run

## Email Setup (Resend.com) (optional)
- Sign up at [resend.com](https://resend.com)
- Get API key from dashboard
- Add to `RESEND_API_KEY` in backend `.env`
- Used for email verification and password reset
