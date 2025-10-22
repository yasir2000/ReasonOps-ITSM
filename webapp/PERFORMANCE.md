# Web App Performance Optimization Guide

## Quick Wins

### 1. Build Optimization
```bash
# Install dependencies
cd webapp
npm install

# Production build
npm run build

# Analyze bundle
npx vite-bundle-visualizer
```

### 2. Code Splitting Example
```typescript
// Instead of:
import DashboardPage from './pages/DashboardPage'

// Use:
const DashboardPage = lazy(() => import('./pages/DashboardPage'))

// Wrap routes with Suspense:
<Suspense fallback={<LoadingSkeleton />}>
  <DashboardPage />
</Suspense>
```

### 3. Memo Expensive Calculations
```typescript
import { useMemo } from 'react'

const ExpensiveComponent = ({ data }) => {
  const processedData = useMemo(() => {
    return data.map(item => /* expensive operation */)
  }, [data])
  
  return <div>{/* render */}</div>
}
```

### 4. Optimize Images
```html
<!-- Use modern formats -->
<picture>
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="Description" loading="lazy">
</picture>
```

### 5. Vite Configuration
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'chart-vendor': ['chart.js'],
        }
      }
    }
  }
})
```

## Performance Metrics

### Target Metrics
- **First Contentful Paint (FCP)**: < 1.8s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Time to Interactive (TTI)**: < 3.8s
- **Total Blocking Time (TBT)**: < 200ms
- **Cumulative Layout Shift (CLS)**: < 0.1

### Lighthouse Audit
```bash
npm run build
npm run preview
# Open Chrome DevTools > Lighthouse > Run Audit
```

## Network Optimization

### 1. Enable Compression
```nginx
# nginx.conf
gzip on;
gzip_types text/css application/javascript application/json;
gzip_min_length 1000;
```

### 2. Cache Headers
```nginx
location /assets/ {
  expires 1y;
  add_header Cache-Control "public, immutable";
}
```

### 3. CDN Integration
```bash
# Upload build to CDN
aws s3 sync dist/ s3://your-bucket/ --cache-control max-age=31536000
```

## Runtime Optimization

### 1. Debounce Search/Filter
```typescript
import { useMemo, useState } from 'react'

const useDebounce = (value: string, delay: number) => {
  const [debouncedValue, setDebouncedValue] = useState(value)
  
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(handler)
  }, [value, delay])
  
  return debouncedValue
}
```

### 2. Virtual Scrolling
```bash
npm install @tanstack/react-virtual
```

```typescript
import { useVirtualizer } from '@tanstack/react-virtual'

const VirtualList = ({ items }) => {
  const parentRef = useRef<HTMLDivElement>(null)
  
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  })
  
  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualizer.getVirtualItems().map(virtualRow => (
          <div key={virtualRow.index}>{items[virtualRow.index]}</div>
        ))}
      </div>
    </div>
  )
}
```

### 3. Optimize Re-renders
```typescript
import { memo } from 'react'

const ExpensiveComponent = memo(({ data }) => {
  // Component implementation
}, (prevProps, nextProps) => {
  // Custom comparison
  return prevProps.data.id === nextProps.data.id
})
```

## Monitoring

### 1. Web Vitals
```bash
npm install web-vitals
```

```typescript
// reportWebVitals.ts
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

getCLS(console.log)
getFID(console.log)
getFCP(console.log)
getLCP(console.log)
getTTFB(console.log)
```

### 2. Error Tracking
```bash
npm install @sentry/react
```

```typescript
import * as Sentry from '@sentry/react'

Sentry.init({
  dsn: 'YOUR_SENTRY_DSN',
  integrations: [new Sentry.BrowserTracing()],
  tracesSampleRate: 1.0,
})
```

### 3. Analytics
```typescript
// Analytics wrapper
export const trackEvent = (event: string, data?: Record<string, any>) => {
  if (typeof window.gtag !== 'undefined') {
    window.gtag('event', event, data)
  }
}
```

## Checklist

### Before Deployment
- [ ] Run Lighthouse audit (score > 90)
- [ ] Test on slow 3G network
- [ ] Test on low-end devices
- [ ] Check bundle size (< 500KB gzipped)
- [ ] Enable compression (gzip/brotli)
- [ ] Set cache headers
- [ ] Optimize images (WebP, lazy loading)
- [ ] Remove console.logs
- [ ] Enable source maps (separate files)
- [ ] Test error boundary
- [ ] Verify accessibility (WAVE, axe)

### After Deployment
- [ ] Monitor error rates
- [ ] Track Core Web Vitals
- [ ] Check CDN hit rates
- [ ] Review server logs
- [ ] Test rollback procedure

## Common Issues

### Issue: Large Bundle Size
**Solution**: Code splitting, tree shaking, analyze with bundle visualizer

### Issue: Slow First Load
**Solution**: Lazy load non-critical components, optimize images, enable compression

### Issue: Poor Mobile Performance
**Solution**: Reduce JavaScript, optimize images, test on real devices

### Issue: High Error Rates
**Solution**: Add error boundaries, improve error handling, add monitoring

### Issue: Layout Shifts
**Solution**: Define image dimensions, avoid injecting content, use skeleton screens

## Tools

### Development
- React DevTools
- Redux DevTools
- Chrome DevTools Performance Tab
- Network Throttling
- Lighthouse CI

### Production
- Sentry (Error Tracking)
- DataDog (Monitoring)
- Google Analytics (Usage)
- Cloudflare (CDN + Analytics)
- Vercel Analytics

## Resources

- [web.dev](https://web.dev/metrics/)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)
- [Bundle Phobia](https://bundlephobia.com/)
- [Can I Use](https://caniuse.com/)

---

**Last Updated**: 2024-01-09  
**Maintained By**: ReasonOps Development Team
