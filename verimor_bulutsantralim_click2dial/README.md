============
Verimor Bulutsantralim Click2dial
============

API Dokümantasyonu: https://github.com/verimor/Bulutsantralim-API


Bilinen Hatalar / Yol Haritası:

* Arama aksiyonundan sonra mailbox_inbox modülüne yönlendiriyor.
* _start_call_verimor fonksiyonu asenkron çalışması lazım. (bkz. queue_job)
* İşlevsel diğer api fonksiyonlarının eklenmesi.