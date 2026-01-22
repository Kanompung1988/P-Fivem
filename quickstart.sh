#!/bin/bash

# Quick Start Script - ทดสอบระบบอย่างรวดเร็ว

echo "🚀 Quick Start - Seoulholic Chatbot + Facebook Integration"
echo "=========================================================="
echo ""

# 1. ตรวจสอบไฟล์ .env
if [ ! -f .env ]; then
    echo "📋 สร้างไฟล์ .env..."
    cp .env.example .env
    echo "✅ สร้างแล้ว - กรุณาแก้ไขไฟล์ .env และใส่ค่า API Keys"
fi

# 2. ติดตั้ง dependencies
echo ""
echo "📦 ติดตั้ง dependencies..."
pip install -q -r streamlit_demo/requirements.txt

# 3. อัปเดตข้อมูลจาก Facebook ครั้งแรก
echo ""
echo "📥 ดึงข้อมูลจาก Facebook (ครั้งแรก)..."
python facebook_integration/auto_updater.py once

# 4. รัน Streamlit
echo ""
echo "🌐 เริ่ม Chatbot Web App..."
echo "ℹ️  เปิดเบราว์เซอร์ที่ http://localhost:8501"
echo "ℹ️  กด Ctrl+C เพื่อหยุด"
echo ""

streamlit run streamlit_demo/app.py
