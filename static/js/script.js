function submitToWhatsApp() {
    const formData = {
        name: document.getElementById('name').value,
        phone: document.getElementById('phone').value,
        carType: document.getElementById('carType').value,
        rentalDate: document.getElementById('rentalDate').value,
        rentalPeriod: document.getElementById('rentalPeriod').value,
        location: document.getElementById('location').value
    };
    
    for (let key in formData) {
        if (!formData[key]) {
            alert('يرجى تعبئة جميع الحقول المطلوبة');
            return;
        }
    }
    
    const message = `طلب تأجير سيارة جديد%0A%0A` +
        `👤 الاسم: ${formData.name}%0A` +
        `📞 رقم الهاتف: ${formData.phone}%0A` +
        `🚗 نوع السيارة: ${formData.carType}%0A` +
        `📅 تاريخ التأجير: ${formData.rentalDate}%0A` +
        `⏰ مدة التأجير: ${formData.rentalPeriod}%0A` +
        `📍 موقع التسليم: ${formData.location}`;
    
    const adminPhone = "966500000000";
    const whatsappURL = `https://wa.me/${adminPhone}?text=${message}`;
    window.open(whatsappURL, '_blank');
}
