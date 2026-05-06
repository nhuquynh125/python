# Travel Social Network - Demo Project

A Vietnamese travel social network platform where users can share travel experiences about Vietnamese landmarks.

## Quick Overview

**What it does:**
- Users signup/login with Google OAuth or phone SMS OTP
- Create posts about travel experiences to specific Vietnamese landmarks
- Like posts with emotions (❤️, 😂, 😲, 😢, 🤩)
- View feed with posts from all users
- Edit user profile and follow friends

**Tech Stack:**
- **Frontend**: HTML5 + CSS3 (Responsive) + Vanilla JavaScript (ES6+)
- **Backend**: Flask (Python) with SQLAlchemy ORM
- **Database**: SQLite
- **API**: RESTful with FormData for file uploads

## Quick Start

### 🚀 Option 1: Use the batch script (Windows)

```powershell
# Double-click start.cmd in this folder
# Choose option 5 for full setup (both servers)
```

### 🚀 Option 2: Manual setup (any OS)

**Terminal 1 - Backend:**
```bash
cd TravelSocialNetwork/backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt
python db_init.py
flask run
```

**Terminal 2 - Frontend:**
```bash
cd TravelSocialNetwork/frontend
python -m http.server 8000
# Open browser: http://localhost:8000/index.html
```

## Project Structure

```
TravelSocialNetwork/
├── frontend/                 # User interface
│   ├── index.html           # Login page
│   ├── signup.html          # Registration
│   ├── dashboard.html       # Main feed
│   ├── create-post.html     # New post page
│   ├── profile.html         # User profile
│   ├── api.js              # API client (main integration layer)
│   ├── script.js           # Login logic
│   ├── signup.js           # Signup logic
│   ├── dashboard.js        # Feed logic
│   ├── create-post.js      # Post creation logic
│   ├── profile.js          # Profile logic
│   └── style.css           # Responsive styling
│
├── backend/                  # Server & API
│   ├── app.py              # Flask app setup
│   ├── models.py           # Database models
│   ├── auth.py             # Auth endpoints
│   ├── posts.py            # Posts endpoints
│   ├── db_init.py          # Initialize database
│   ├── test_integration.py # Automated tests
│   ├── requirements.txt     # Python dependencies
│   └── README.md           # Backend docs
│
├── SETUP_GUIDE.md          # Detailed setup instructions
└── start.cmd               # Quick start script (Windows)
```

## Features

### Authentication
- ✓ Email + password signup with validation
- ✓ Login with email/password
- ✓ Phone OTP (demo - sends fake OTP to console)
- ⚠️ Google OAuth (placeholder - needs configuration)

### Posts
- ✓ Create posts with content, location, mood, images
- ✓ View all posts in feed
- ✓ Like posts with 5 emotions (❤️ 😂 😲 😢 🤩)
- ✓ Image upload (up to 5 images per post)

### User Features
- ✓ User profile with stats
- ✓ Edit profile info
- ⚠️ Follow/unfollow users (UI ready, backend scaffolded)
- ⚠️ Comments (UI ready, backend scaffolded)

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/signup` | Create new user |
| POST | `/api/auth/login` | Login with email/password |
| POST | `/api/auth/phone/send_otp` | Send OTP to phone |
| POST | `/api/auth/phone/verify` | Verify phone OTP |
| GET | `/api/posts` | List all posts |
| POST | `/api/posts` | Create new post |
| GET | `/api/posts/<id>` | Get single post |
| POST | `/api/posts/<id>/like` | Like/unlike post |

## Testing

### Manual Testing
1. Signup at login page
2. Login with created credentials
3. Create a post with image
4. Like posts from other users
5. Edit your profile

### Automated Testing
```bash
cd backend
python test_integration.py
```

This will test all API endpoints automatically.

## Responsive Design

Works on all screen sizes:
- 📱 Mobile (320px+)
- 📱 Tablet (600px+)
- 💻 Laptop (1200px+)

## Known Limitations

- **Auth**: Uses localStorage (demo only) - should use JWT for production
- **OTP**: Sends fake code to console - needs Twilio integration
- **OAuth**: Google login is placeholder - needs Google API setup
- **Database**: SQLite (fine for demo) - should use PostgreSQL for production
- **Uploads**: Local `uploads/` folder (should use cloud storage like S3)

## For Production

- Add JWT token authentication
- Integrate Twilio for real SMS OTP
- Setup Google OAuth properly
- Move to PostgreSQL database
- Use cloud storage (S3, Azure Blob, etc.)
- Add Docker containerization
- Setup CI/CD pipeline
- Deploy to cloud (Heroku, AWS, Azure, etc.)

## Vietnamese Landmarks Included

The platform supports these Vietnamese landmarks:
- 🏞️ Vịnh Hạ Long (Ha Long Bay)
- 🏔️ Sapa - Fansipan
- 🏛️ Hà Nội - Hoàn Kiếm Lake
- 🏖️ Đà Nẵng - Mỹ Khánh
- 🏺 Hội An - Ancient Town
- 🏰 Huế - Thừa Thiên Huế
- 🌾 Ruộng bậc thang (Terraced Fields)
- ... and more

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

Demo project for educational purposes.

## Next Steps

1. ✅ Complete frontend-backend integration (DONE)
2. Add JWT authentication
3. Implement friends/follow system
4. Add comments feature
5. Deploy to cloud
6. Mobile app version

---

**Questions?** Check SETUP_GUIDE.md for detailed instructions.

**Found a bug?** Update the code and test with test_integration.py.

Chúc mừng! (Happy coding! 🚀)
