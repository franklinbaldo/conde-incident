import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

// No global console interceptors or Google Maps auth hooks:
// the orbital map renders with local SVG geometry and no external key.
createRoot(document.getElementById('root')!).render(<App />);
