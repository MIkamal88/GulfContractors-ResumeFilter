# Gulf Contractors Resume Filter - Frontend

A modern, responsive React + TypeScript frontend for the Gulf Contractors Resume Filter application.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Axios** - HTTP client for API communication
- **CSS3** - Modern styling with responsive design

## Features

- Drag-and-drop file upload for resumes (PDF, DOCX)
- Dynamic keyword input with tag management
- Real-time resume analysis with progress feedback
- Beautiful results display with:
  - Score visualization (color-coded: high/medium/low)
  - Matched keywords highlighting
  - AI-generated summaries
  - Pass/fail statistics
- CSV export functionality
- Fully responsive design for mobile and desktop
- Error handling and user feedback

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── FileUpload.tsx      # Drag-and-drop file uploader
│   │   ├── KeywordInput.tsx    # Keyword tag input
│   │   └── Results.tsx         # Results display component
│   ├── services/
│   │   └── api.ts              # API service layer
│   ├── types/
│   │   └── index.ts            # TypeScript type definitions
│   ├── App.tsx                 # Main application component
│   ├── App.css                 # Application styles
│   ├── index.css               # Global styles
│   └── main.tsx                # Application entry point
├── Dockerfile                   # Production Docker configuration
├── nginx.conf                   # Nginx configuration for production
├── vite.config.ts              # Vite configuration
└── package.json                # Dependencies and scripts
```

## Development

### Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

### Installation

```bash
cd frontend
npm install
```

### Running Locally

```bash
npm run dev
```

The app will be available at http://localhost:5173

The dev server includes a proxy that forwards `/api` requests to the backend at `http://localhost:8000`.

### Building for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Docker Deployment

### Development Mode

The development docker-compose configuration serves the frontend through Nginx:

```bash
# From project root
docker-compose -f docker-compose.dev.yml up -d
```

Access at: http://localhost:3000

### Production Mode

```bash
# From project root
docker-compose -f docker-compose.prod.yml up -d
```

Access at: http://localhost:3000

## API Integration

The frontend communicates with the backend through the `/api` endpoint:

- **POST /api/filter-resumes** - Upload and filter multiple resumes
- **POST /api/analyze-single** - Analyze a single resume
- **GET /api/download-csv** - Download CSV results

### API Service (`src/services/api.ts`)

Provides three main functions:

1. `filterResumes(files, keywords, minScore, generateAiSummary)` - Filter multiple resumes
2. `analyzeSingleResume(file, keywords, generateAiSummary)` - Analyze single resume
3. `downloadCSV(filePath)` - Download CSV report

## Environment Variables

### Development (`.env.development`)

```env
VITE_API_URL=/api
```

### Production (`.env.production`)

```env
VITE_API_URL=/api
```

The `/api` path is proxied to the backend by Nginx in production and Vite dev server in development.

## Component Documentation

### FileUpload

Handles file selection through drag-and-drop or file picker.

**Props:**
- `onFilesSelected: (files: File[]) => void` - Callback when files are selected
- `accept?: string` - File types to accept (default: `.pdf,.docx`)
- `multiple?: boolean` - Allow multiple files (default: `true`)

### KeywordInput

Tag-based keyword input component.

**Props:**
- `keywords: string[]` - Current keywords array
- `onKeywordsChange: (keywords: string[]) => void` - Callback when keywords change

**Usage:**
- Press Enter to add a keyword
- Click × to remove a keyword
- Press Backspace on empty input to remove last keyword

### Results

Displays analysis results with statistics and detailed resume information.

**Props:**
- `results: ResumeAnalysis[]` - Array of resume analysis results
- `totalResumes: number` - Total number of resumes processed
- `passedResumes: number` - Number of resumes that passed the filter
- `csvPath?: string` - Path to CSV file
- `onDownloadCSV?: () => void` - Callback for CSV download

## Styling

The application uses custom CSS with:
- CSS Grid and Flexbox for layouts
- CSS custom properties for theming
- Responsive design with media queries
- Modern gradient backgrounds
- Smooth transitions and hover effects

### Color Scheme

- Primary: `#667eea` to `#764ba2` (purple gradient)
- Success: `#4caf50` (green)
- Warning: `#f57c00` (orange)
- Error: `#c62828` (red)
- Background: `#f5f7fa` (light gray)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance Optimizations

- Code splitting with Vite
- Lazy loading of components
- Optimized bundle size with tree shaking
- Gzip compression in production (Nginx)
- Static asset caching
- Image optimization

## Troubleshooting

### API Connection Issues

If the frontend can't connect to the backend:

1. Check that the backend is running on port 8000
2. Verify the VITE_API_URL environment variable
3. Check browser console for CORS errors
4. Ensure Nginx proxy configuration is correct (production)

### Build Errors

```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

### Type Errors

Make sure TypeScript imports use `type` keyword for type-only imports:

```typescript
import type { MyType } from './types';
```

## Future Enhancements

- [ ] Dark mode support
- [ ] Advanced filtering options
- [ ] Resume comparison feature
- [ ] Export to multiple formats (Excel, PDF)
- [ ] User authentication
- [ ] Resume history and saved searches
- [ ] Batch operations
- [ ] Real-time progress updates with WebSockets

## License

Proprietary - Gulf Contractors
