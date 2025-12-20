# RescueWorks Frontend

React frontend for the RescueWorks animal rescue management system, optimized for Vercel deployment.

## Features

- **Sprint 1**: Animal intake forms with photo upload
- **Sprint 2**: Foster coordinator dashboard with automated matching
- **Sprint 3**: Operations dashboard with reports and search
- **Sprint 4**: Admin panel for user and system management

## Tech Stack

- React 18
- Vite
- Axios for API calls
- Modern CSS with responsive design

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Deployment to Vercel

### Via GitHub (Recommended)

1. Push code to GitHub
2. Import repository to Vercel
3. Configure build settings:
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. Set environment variable:
   - `VITE_API_URL`: Your Railway backend URL
5. Deploy!

### Via CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

## Environment Variables

Create a `.env` file:

```
VITE_API_URL=http://localhost:8000  # For local development
# or
VITE_API_URL=https://your-backend.railway.app  # For production
```

## Pages

- **Dashboard**: Overview of operations with key metrics
- **Animals**: Animal management with intake form and photo upload
- **Foster Management**: Foster profiles, matching algorithm, and placements
- **Operations**: Care updates, search/filter, and reports
- **Admin**: User management, system config, and organization info

## API Integration

All API calls are centralized in `src/utils/api.js` using Axios. The API client:
- Automatically adds JWT tokens to requests
- Handles request/response transformations
- Provides typed API functions

## Authentication

The app uses JWT token authentication:
- Tokens are stored in localStorage
- Automatically added to API requests
- User redirected to login if token is invalid

## Responsive Design

The app is fully responsive with:
- Mobile-first CSS approach
- Flexible grid layouts
- Touch-friendly UI elements

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Contributing

See main README.md for contribution guidelines.
