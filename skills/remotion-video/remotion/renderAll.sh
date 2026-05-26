#!/bin/bash
set -e

echo "Rendering Hexa AI Agency highlight videos..."
echo "============================================="

mkdir -p out

npx remotion render src/index.ts Results out/results.mp4 --codec=h264
echo "✓ Results done"

npx remotion render src/index.ts Services out/services.mp4 --codec=h264
echo "✓ Services done"

npx remotion render src/index.ts HowItWorks out/how-it-works.mp4 --codec=h264
echo "✓ HowItWorks done"

npx remotion render src/index.ts FAQ out/faq.mp4 --codec=h264
echo "✓ FAQ done"

npx remotion render src/index.ts BookACall out/book-a-call.mp4 --codec=h264
echo "✓ BookACall done"

echo ""
echo "✅ All 5 highlight videos rendered to out/"
ls -lh out/*.mp4
