#!/usr/bin/env node
/**
 * Bundle Size Analysis Script
 * 
 * Analyzes the production build and reports bundle sizes
 */

const fs = require('fs');
const path = require('path');

const distDir = path.join(__dirname, '../dist');
const assetsDir = path.join(distDir, 'assets');

function getFileSize(filePath) {
  const stats = fs.statSync(filePath);
  return stats.size;
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

function analyzeBundle() {
  console.log('\n' + '='.repeat(70));
  console.log('📊 BUNDLE SIZE ANALYSIS');
  console.log('='.repeat(70) + '\n');

  if (!fs.existsSync(distDir)) {
    console.error('❌ dist directory not found. Run "yarn build" first.');
    process.exit(1);
  }

  if (!fs.existsSync(assetsDir)) {
    console.error('❌ assets directory not found in dist.');
    process.exit(1);
  }

  const files = fs.readdirSync(assetsDir);
  
  const jsFiles = files.filter(f => f.endsWith('.js'));
  const cssFiles = files.filter(f => f.endsWith('.css'));
  
  let totalJS = 0;
  let totalCSS = 0;

  console.log('📦 JavaScript Bundles:\n');
  jsFiles.forEach(file => {
    const size = getFileSize(path.join(assetsDir, file));
    totalJS += size;
    
    const sizeFormatted = formatBytes(size);
    const sizeKB = size / 1024;
    
    let icon = '✅';
    if (sizeKB > 500) icon = '⚠️ ';
    if (sizeKB > 1000) icon = '❌';
    
    console.log(`   ${icon} ${file}: ${sizeFormatted}`);
  });

  console.log('\n🎨 CSS Files:\n');
  cssFiles.forEach(file => {
    const size = getFileSize(path.join(assetsDir, file));
    totalCSS += size;
    console.log(`   ✅ ${file}: ${formatBytes(size)}`);
  });

  console.log('\n' + '-'.repeat(70));
  console.log('📊 Summary:\n');
  console.log(`   Total JS:  ${formatBytes(totalJS)}`);
  console.log(`   Total CSS: ${formatBytes(totalCSS)}`);
  console.log(`   Total:     ${formatBytes(totalJS + totalCSS)}`);
  console.log('-'.repeat(70));

  // Performance warnings
  console.log('\n💡 Recommendations:\n');
  
  const totalKB = (totalJS + totalCSS) / 1024;
  
  if (totalKB < 500) {
    console.log('   ✅ Excellent: Bundle size is optimal (< 500KB)');
  } else if (totalKB < 1000) {
    console.log('   ⚠️  Good: Bundle size is acceptable (< 1MB)');
    console.log('   Consider code-splitting for further optimization');
  } else if (totalKB < 2000) {
    console.log('   ⚠️  Warning: Bundle size is large (> 1MB)');
    console.log('   Recommended actions:');
    console.log('   - Enable code-splitting');
    console.log('   - Lazy load heavy components');
    console.log('   - Check for duplicate dependencies');
  } else {
    console.log('   ❌ Critical: Bundle size is too large (> 2MB)');
    console.log('   Immediate actions required:');
    console.log('   - Analyze with bundle analyzer');
    console.log('   - Remove unused dependencies');
    console.log('   - Implement aggressive code-splitting');
  }

  console.log('\n' + '='.repeat(70) + '\n');

  // Exit with warning if bundle is too large
  if (totalKB > 2000) {
    process.exit(1);
  }
}

try {
  analyzeBundle();
} catch (error) {
  console.error('❌ Analysis failed:', error);
  process.exit(1);
}
