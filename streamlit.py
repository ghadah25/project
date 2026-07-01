import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np



# إعدادات الصفحة العامة لجعل المظهر مريحاً واحترافياً
st.set_page_config(page_title="لوحة تحليل البيانات الإبداعية", layout="wide")

st.title("📊 لوحة تحكم وتحليل البيانات التفاعلية")
st.markdown("قم برفع ملف الإكسل الخاص بك واستمتع بالتحليلات الفورية والتنظيف التلقائي للبيانات!")

# 1. شريط جانبي لرفع الملف والفلاتر
st.sidebar.header("📁 مدخلات البيانات والفلاتر")
uploaded_file = st.sidebar.file_uploader("اختر ملف إكسل (Excel)", type=["xlsx", "csv"])

if uploaded_file is not None:
    # قراءة البيانات
  if uploaded_file is not None:
    # يجب أن تكون هناك مسافة بادئة (Tab) قبل كلمة try لتصبح داخل الـ if
    try:
        df = pd.read_excel(uploaded_file)
    except Exception:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
    
    # باقي كود التنظيف يستمر بنفس مستوى المسافة بالداخل...
    if 'City' in df.columns:
        df['City'] = df['City'].astype(str).str.strip().str.capitalize()
    # ... إلخ
    
    # --- خطوة التنظيف التلقائي والإبداعي خلف الكواليس ---
    # أ: توحيد أسماء المدن تلقائياً (إزالة المسافات وتوحيد حالة الأحرف)
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
    st.sidebar.subheader("🔍 تصفية وفلترة البيانات")
    
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
    
    # تصميم بطاقات ذكية للأرقام القياسية (KPIs) لتعطي لمسة إبداعية
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

    # تقسيم الصفحة إلى جزأين لعرض الجدول بجانب الرسم البياني
    main_col1, main_col2 = st.columns([1, 1])

    with main_col1:
        st.subheader("📋 نظرة على البيانات المنظّفة والمنقحة")
        st.dataframe(df, use_container_width=True)

    with main_col2:
        st.subheader("🎯 التوزيع الجغرافي للمدن (بعد التوحيد)")
        if 'City' in df.columns and not df.empty:
            city_counts = df['City'].value_counts()
         # تأكدي من استيراد المكتبة في أعلى الملف: import plotly.express as px

st.subheader("🎯 التوزيع الجغرافي للمدن بألوان فريدة")
if 'City' in df.columns and not df.empty:
    # 1. تجهيز تكرارات المدن
    city_counts = df['City'].value_counts().reset_index()
    city_counts.columns = ['City', 'Count']
    
    # 2. إنشاء المخطط الذكي متعدد الألوان تلقائياً
    fig = px.pie(city_counts, 
                 values='Count', 
                 names='City', 
                 hole=0.3, # يجعله دونات أنيق وعصري
                 color='City', # السحر هنا: هذا السطر يعطي كل مدينة لوناً فريداً وخاصاً بها
                 color_discrete_sequence=px.colors.qualitative.Set3) # مجموعة ألوان مبهجة ومتنوعة لكل المدن

    fig.update_traces(textposition='inside', textinfo='percent+label')

    # 3. عرض المخطط التفاعلي الجديد في ستريم ليت
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("لا توجد بيانات كافية لعرض المخطط البياني.")
            
            # تمرير الرسمة لـ Streamlit
            st.pyplot(fig)
        else:
            st.warning("لا توجد بيانات كافية لعرض المخطط البياني.")

else:
    # رسالة تظهر للمستخدم تطلب منه رفع الملف أولاً
    st.info("💡 بانتظار رفع ملف الإكسل من الشريط الجانبي لبدء السحر والتحليل!")
