# miniproject07
ETL workshop by using GCP & Apache airflow
สร้าง Project ในการทำ Data Pipeline แบบง่ายๆ โดยดึงข้อมูลจาก MySql และ Api เพื่อนำข้อมูลมา merge กันแล้ว Transform ข้อมูลมาเก็บลงบน Data Lake(Google Cloud Storage) จากนั้นนำข้อมูลที่อยู่ใน Data Lake ส่งไปที่ Data warehouse(Google BigQuery)
 
step 1 : สร้าง Airflow โดยใน GCP จะสามารถใช้ Airflow ผ่าน Cloud Composer โดยเข้า console.cloud.google.com ทำการสร้างโปรเจกต์ แล้ว create composer environment โดยใช้ composer2
![image](https://github.com/nechayut/miniproject07/assets/101554284/0f5f672b-caf6-471b-a103-1d7dbe091351)
![image](https://github.com/nechayut/miniproject07/assets/101554284/bced06c9-b862-4592-a58a-57e2a39d143d)

เมื่อสร้าง composer environment สำเร็จจะขึ้นเครื่องหมายถูกด้านหน้าชื่อ environment, 
Bucket ของ Composer จะถูกสร้างอัตโนมัติ ใน GCS และจะถูก mount กับ folder ของ Airflow
![image](https://github.com/nechayut/miniproject07/assets/101554284/d1d96436-3887-4819-bae7-dd9632a19640)




step 2 : ทำการลง Python packages ที่จะใช้ในโปรเจกต์ให้เรียบร้อย โดยเลือก PYPI PACKAGES ในหน้า Environment detail กด edit และใส่ package ที่จะใช้ โดยใน project นี้จะใช้ requests, pymysql, pandas ในการจัดการกับข้อมูล

![image](https://github.com/nechayut/miniproject07/assets/101554284/8b7980bc-3b2c-4837-8036-24ba77de1643)




step 3 : ต่อ connection กับ MySql โดยเข้าหน้า Airflow Web UI แล้วเลือก Admin > connections แล้ว edit connection และใส่ข้อมูล connection ที่เราจะเชื่อมต่อ (Host, Schema, Login, Password, Port)

![image](https://github.com/nechayut/miniproject07/assets/101554284/2594d807-a9ae-47dd-bb4e-f6f4ef44886d)
![image](https://github.com/nechayut/miniproject07/assets/101554284/1f12ecf3-6c73-4891-a0f3-66b80ea1b411)




step 4 : สร้าง Dataset ใน Google BigQuery โดยเลือก region เดียวกับ Composer Environment เพื่อใช้ในการเก็บ Table ที่จะส่งเข้าไป โดย Project นี้ใช้ region เป็น us-central1

![image](https://github.com/nechayut/miniproject07/assets/101554284/c803c9ba-2745-4784-9b47-8f6bafbf9b4c)




step 5 : ทำการ upload file.py(แนบไฟล์ไว้ด้านบน) ที่จะใช้ในการสร้าง DAG ของ Pipeline นี้ลงใน folder dags ใน bucket ของ composer environment
![image](https://github.com/nechayut/miniproject07/assets/101554284/08ea579a-941a-48d8-93ea-fe6317ac9b2b)


รอสักครู่แล้ว DAG ใหม่จะโชว์ในหน้าAirflow Web UI พร้อมกับ run DAG ในครั้งแรก
![image](https://github.com/nechayut/miniproject07/assets/101554284/ce3d2e33-5934-439a-837a-3442f26f63c2)


โดย Task ใน DAG นี้จะประกอบไปด้วย 4 Task โดย Task1 จะดึงข้อมูลจาก MySql มาเก็บไว้ใน GCS , Task2 จะดึงข้อมูลจาก Api มาเก็บไว้ใน GCS , Task3 merge และ transfrom ข้อมูลแล้วเก็บไว้ใน GCS , Task4 จะนำข้อมูลที่ถูกเก็บไว้ใน GCS นำเข้า Google BigQuery
![image](https://github.com/nechayut/miniproject07/assets/101554284/34220d2f-3692-4ba8-85a1-befb524fe39d)

เมื่อ DAG รันครบลูป(กรอบ task ในหน้า graph เป็นสีเขียวเข้มทั้งหมด) จะพบไฟล์ใน folder DATA ใน bucket ของ composer และจะพบ Table ไปโชว์ใน Dataset ที่สร้างไว้ใน BigQuery
![image](https://github.com/nechayut/miniproject07/assets/101554284/f94d574c-5c19-49b5-a106-df60edae7a2a)
![image](https://github.com/nechayut/miniproject07/assets/101554284/f8bf5167-6cce-44c3-854c-dd91469f6007)

