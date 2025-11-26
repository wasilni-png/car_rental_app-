cat > ~/deploy.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

# ألوان للoutput
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 بدء عملية النشر التلقائي...${NC}"

# الانتقال لمجلد المشروع
cd ~/taxi-waslny

# التحقق من وجود مجلد .git
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ لم يتم العثور على مستودع git!${NC}"
    echo "جاري تهيئة المستودع..."
    git init
    git remote add origin https://github.com/YOUR_USERNAME/taxi-waslny.git
fi

# التحقق من التغييرات
echo -e "${YELLOW}📊 التحقق من التغييرات...${NC}"
git status

# إضافة جميع الملفات
echo -e "${YELLOW}📁 إضافة الملفات...${NC}"
git add .

# إنشاء commit مع timestamp
COMMIT_MSG="Auto-deploy: $(date '+%Y-%m-%d %H:%M:%S')"
echo -e "${YELLOW}💾 إنشاء commit...${NC}"
git commit -m "$COMMIT_MSG"

# رفع التغييرات
echo -e "${YELLOW}☁️ رفع التغييرات إلى GitHub...${NC}"
git branch -M main

# محاولة الرفع (مع معالجة الأخطاء)
if git push -u origin main; then
    echo -e "${GREEN}✅ تم الرفع بنجاح إلى GitHub!${NC}"
    echo -e "${GREEN}📎 الرابط: https://github.com/YOUR_USERNAME/taxi-waslny${NC}"
else
    echo -e "${RED}❌ فشل الرفع! قد تحتاج إلى token.${NC}"
    echo "جاري استخدام token للرفع..."
    
    # استخدام token للرفع (استبدل YOUR_TOKEN وYOUR_USERNAME)
    git push https://YOUR_TOKEN@github.com/YOUR_USERNAME/taxi-waslny.git main
fi

echo -e "${GREEN}🎉 اكتملت عملية النشر!${NC}"
EOF
