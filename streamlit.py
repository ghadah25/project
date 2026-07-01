import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# إعدادات الصفحة العامة لجعل المظهر مريحاً واحترافياً
st.set_page_config(page_title="لوحة تحليل البيانات الإبداعية", layout="wide")

st.title("📊 لوحة تحكم وتحليل البيانات التفاعلية")
st.markdown("استمتع بالتحليلات الفورية والتنظيف التلقائي للبيانات المستدعاة مباشرة من المشروع!")

# اسم ملف البيانات الموجود لديكِ في نفس المجلد (تأكدي من كتابة الاسم والامتداد الصحيح هنا)
# يمكنكِ تغيير 'data.xlsx' لاسم ملفكِ الحقيقي مثل 'data.csv' أو أي اسم آخر
DATA_FILE = 'clean_data.csv' 

# محاولة ذكية لقراءة الملف مباشرة من المستودع بناءً على صيغته
try:
    if not os.path.exists(DATA_FILE):
        # إذا لم يجد ملف الـ Excel، نجرب البحث عن نسخة الـ CSV تلقائياً
        DATA_FILE = DATA_FILE.replace('.xlsx', '.csv')
        
    if DATA_FILE.endswith('.csv'):
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.read_excel(DATA_FILE)
        
    # --- خطوة التنظيف التلقائي والإبداعي خلف الكواليس ---
    
    # أ: توحيد أسماء المدن تلقائياً (إزالة المسافات وتوحيد حالة الأحرف لتندمج التكرارات)
    if 'City' in df.columns:
        df['City'] = df['City'].astype(str).str.strip().str.capitalize()
        
    # ب: معالجة القيم الشاذة والمفقودة في سنوات الخبرة
    if 'Years of Experience' in df.columns:
        # حساب الوسيط باستثناء القيم الشاذة (-1)
        valid_experience = df[df['Years of Experience'] >= 0]['Years of Experience']
        median_exp = valid_experience.median() if not valid_experience.empty else 0
        # استبدال -1 بالوسيط
        df['Years of Experience'] = df['Years of Experience'].replace(-1, median_exp)
        # تعويض القيم المفقودة بالوسيط وتحويلها لأرقام صحيحة
        df['Years of Experience'] = df['Years of Experience'].fillna(median_exp).astype(int)

    # ج: معالجة عمود مستوى الخبرة النصي (تعويض المفقود بالأكثر تكراراً)
    if 'Experience Level' in df.columns:
        df['Experience Level'] = df['Experience Level'].replace(r'^\s*$', np.nan, regex=True)
        if df['Experience Level'].isnull().sum() < len(df):
            most_frequent_level = df['Experience Level'].mode()[0]
            df['Experience Level'] = df['Experience Level'].fillna(most_frequent_level)

    # د: إضافة عمود "التقييم" الإبداعي بناءً على سنوات الخبرة
    if 'Years of Experience' in df.columns and 'التقييم' not in df.columns:
        df['التقييم'] = df['Years of Experience'].apply(lambda x: '⭐⭐⭐⭐⭐ ممتاز' if x > 5 else '⭐⭐⭐ جيد')


    # --- إضافة الفلاتر التفاعلية في الشريط الجانبي ---
    st.sidebar.header("🔍 تصفية وفلترة البيانات")
    
    # فلتر المدن الموحدة
    if 'City' in df.columns:
        all_cities = df['City'].unique().tolist()
        selected_cities = st.sidebar.multiselect("اختر المدن:", options=all_cities, default=all_cities)
        df = df[df['City'].isin(selected_cities)]
        
    # فلتر مستوى الخبرة
    if 'Experience Level' in df.columns:
        all_levels = df['Experience Level'].unique().tolist()
        selected_levels = st.sidebar.multiselect("اختر مستوى الخبرة:", options=all_levels, default=all_levels)
        df = df[df['Experience Level'].isin(selected_levels)]


    # --- عرض النتائج والتحليلات في الصفحة الرئيسية ---
    
    # تصميم بطاقات ذكية للأرقام القياسية (KPIs)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("إجمالي السجلات المفلترة", len(df))
    with col2:
        if 'City' in df.columns:
            st.metric("عدد المدن الفريدة", df['City'].nunique())
    with col3:
        if 'Years of Experience' in df.columns:
            st.metric("متوسط سنوات الخبرة", f"{df['Years of Experience'].mean():.1f} سنة")

    st.markdown("---")

    # تقسيم الصفحة إلى جزأين متناسقين لعرض الجدول بجانب الرسم البياني
    main_col1, main_col2 = st.columns([1, 1.2])

    with main_col1:
        st.subheader("📋 نظرة على البيانات المنظّفة والمنقحة")
        st.dataframe(df, use_container_width=True)

    with main_col2:
        st.subheader("🎯 التوزيع الجغرافي للمدن بألوان فريدة")
        if 'City' in df.columns and not df.empty:
            # 1. تجهيز تكرارات المدن لتناسب Plotly
            city_counts = df['City'].value_counts().reset_index()
            city_counts.columns = ['City', 'Count']
            
            # 2. إنشاء المخطط الذكي متعدد الألوان تلقائياً (دونات أنيق)
            fig = px.pie(city_counts, 
                         values='Count', 
                         names='City', 
                         hole=0.3, 
                         color='City', 
                         color_discrete_sequence=px.colors.qualitative.Set3) # كل مدينة بلون فريد تلقائياً

            fig.update_traces(textposition='inside', textinfo='percent+label')

            # 3. عرض المخطط التفاعلي الجديد في ستريم ليت
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("لا توجد بيانات كافية لعرض المخطط البياني.")

except Exception as e:
    st.error(f"❌ لم يتم العثور على ملف البيانات أو حدث خطأ أثناء القراءة. تأكدي من تسمية الملف بشكل صحيح في الكود. تفاصيل الخطأ: {e}")
