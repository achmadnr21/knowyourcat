# https://superuser.com/questions/1807770/enable-long-paths-on-win-11-home
import os
from flask import Flask, request
from flask_restful import Api, Resource
import numpy as np
import tensorflow as tf
print(tf.__version__)

import keras
print(keras.__version__)
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
import io

# os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

app = Flask(__name__)
api = Api(app)

IMG_HEIGHT = 128
IMG_WIDTH = 128
MODEL_PATH = 'model/Regularized_Mobilenetv2_model-21-06-07-51-47.h5'
MODEL = load_model(MODEL_PATH)

PET_FACTS = [
    ['Kucing Abyssinian dikenal sebagai salah satu ras kucing domestik tertua dan paling elegan, sering kali disebut-sebut berasal dari Mesir Kuno. Kucing ini memiliki tubuh yang ramping, otot yang kuat, dan mantel bulu pendek dengan pola warna "ticked" yang khas, di mana setiap helai bulu memiliki beberapa warna. Abyssinian terkenal akan kecerdasan, keaktifan, dan sifatnya yang penasaran serta ramah. Mereka cenderung sangat sosial dan menikmati interaksi dengan manusia, menjadikannya hewan peliharaan yang menyenangkan dan penuh energi. Kucing ini membutuhkan stimulasi mental dan fisik yang cukup untuk tetap bahagia dan sehat.'],
    ['Kucing Bengal adalah hasil persilangan antara kucing domestik dan kucing macan tutul Asia, memberikan mereka penampilan eksotis dengan pola bulu yang menyerupai macan tutul, biasanya berbintik atau berbentuk roset. Ras ini dikenal karena kecerdasan, keaktifan, dan sifat penasaran yang tinggi, sering menikmati bermain dan berinteraksi dengan manusia serta hewan lain. Kucing Bengal memiliki tubuh yang berotot dan kuat, serta mantel bulu yang pendek dan halus, yang sering kali tampak mengilap di bawah cahaya. Mereka membutuhkan banyak stimulasi fisik dan mental serta lingkungan yang dinamis untuk menghindari kebosanan dan perilaku destruktif. Bengal juga dikenal sebagai kucing yang cukup vokal dan suka berkomunikasi dengan pemiliknya.'],
    ['Kucing Birman, juga dikenal sebagai "Kucing Suci dari Burma," adalah ras kucing yang elegan dengan ciri khas bulu semi-panjang yang lembut dan pola warna titik (pointed pattern) seperti pada kucing Siam, namun dengan kaki yang berwarna putih seperti memakai sarung tangan. Mereka memiliki mata biru yang menawan dan tubuh yang berotot namun anggun. Kucing Birman dikenal memiliki sifat yang lembut, ramah, dan penuh kasih sayang, menjadikannya hewan peliharaan yang ideal untuk keluarga. Mereka umumnya bersifat tenang, suka berada di dekat manusia, dan menikmati interaksi sosial, namun tidak terlalu menuntut perhatian. Kucing Birman juga cukup cerdas dan mudah dilatih, menjadikannya cocok untuk pemilik yang menginginkan kucing yang penurut dan berkepribadian menyenangkan.'],
    ['Kucing Bombay adalah ras kucing yang dikenal karena penampilannya yang mirip dengan panther miniatur, dengan bulu hitam pekat yang mengilap dan mata berwarna tembaga atau emas yang kontras. Diciptakan pada tahun 1950-an melalui persilangan antara kucing Burma dan kucing American Shorthair, kucing Bombay memiliki tubuh berotot dan proporsional. Ras ini terkenal dengan sifatnya yang ramah, sosial, dan penuh kasih sayang, serta cenderung membentuk ikatan yang kuat dengan pemiliknya. Mereka suka bermain dan cukup aktif, tetapi juga bisa menjadi kucing pangkuan yang menikmati waktu santai bersama keluarga. Kucing Bombay memiliki suara yang lembut dan tidak terlalu vokal, menjadikannya hewan peliharaan yang ideal untuk lingkungan rumah yang tenang.'],
    ['Kucing British Shorthair adalah salah satu ras kucing tertua dan paling populer di Inggris, dikenal dengan tubuhnya yang kekar, bulat, dan wajah yang menggemaskan dengan pipi tembam serta mata besar yang bulat. Mantel bulunya yang tebal dan mewah hadir dalam berbagai warna, meskipun yang paling terkenal adalah warna biru keabu-abuan yang disebut "British Blue." British Shorthair memiliki sifat yang tenang, ramah, dan mudah bergaul, menjadikannya hewan peliharaan yang ideal untuk keluarga atau individu. Mereka cenderung mandiri tetapi tetap menikmati kehadiran manusia, meskipun tidak terlalu suka digendong atau dipangku. Ras ini juga dikenal sehat dan memiliki harapan hidup yang cukup panjang, dengan sedikit masalah kesehatan genetik dibandingkan beberapa ras lainnya.'],
    ['Kucing Egyptian Mau adalah salah satu ras kucing domestik tertua dan dikenal sebagai satu-satunya kucing yang memiliki pola bintik alami. Mereka memiliki tubuh yang anggun dan berotot dengan bulu pendek yang mengilap, serta kaki belakang yang lebih panjang dari kaki depan, memberikan mereka kemampuan lari yang luar biasa. Mata hijau besar mereka menambah ekspresi wajah yang waspada dan penuh perhatian. Egyptian Mau dikenal dengan sifatnya yang penuh energi, cerdas, dan setia, sering kali membentuk ikatan kuat dengan pemiliknya. Mereka juga cenderung vokal, menggunakan suara dan gerakan ekor untuk berkomunikasi. Selain itu, kucing ini sangat aktif dan membutuhkan banyak stimulasi fisik serta mental untuk tetap bahagia.'],
    ['Kucing Maine Coon adalah salah satu ras kucing domestik terbesar, dikenal dengan tubuhnya yang besar dan berotot, serta mantel bulu panjang yang tebal dan tahan air. Mereka memiliki ekor panjang dan berbulu lebat, serta telinga besar yang sering kali berumbai di ujungnya, memberikan mereka penampilan yang mengesankan. Maine Coon memiliki sifat yang ramah, lembut, dan mudah bergaul, membuat mereka sangat cocok sebagai hewan peliharaan keluarga. Mereka cerdas dan dapat dengan mudah dilatih untuk melakukan trik sederhana atau menggunakan mainan interaktif. Maine Coon juga dikenal suka bermain dengan air dan memiliki suara yang lembut serta khas, sering kali berupa kicauan atau trilling daripada mengeong biasa. Ras ini sangat adaptif dan bisa hidup di berbagai lingkungan, selama mereka mendapatkan perhatian dan stimulasi yang cukup.'],
    ['Kucing Persia adalah salah satu ras kucing yang paling dikenal dan dihargai di dunia, terkenal dengan wajah bulatnya yang datar, hidung pesek, serta bulu panjang dan mewah yang membutuhkan perawatan rutin. Mereka memiliki tubuh yang kekar dan kaki pendek yang memberikan penampilan anggun dan menggemaskan. Kucing Persia dikenal dengan sifatnya yang tenang, manis, dan penuh kasih sayang, sering kali lebih suka beristirahat di tempat nyaman daripada berlari-lari atau memanjat. Mereka cenderung menjadi hewan peliharaan yang santai, menikmati perhatian dan waktu bersama pemiliknya, tetapi tidak terlalu menuntut. Kucing Persia membutuhkan perawatan rutin untuk menjaga kebersihan dan kesehatan bulu mereka yang tebal, serta perhatian khusus terhadap kesehatan mata dan hidung karena bentuk wajahnya yang khas.'],
    ['Kucing Ragdoll adalah ras kucing yang dikenal karena sifatnya yang sangat tenang dan penyayang, serta kecenderungannya untuk rileks sepenuhnya ketika dipegang, seperti boneka kain, yang memberi mereka nama "Ragdoll." Mereka memiliki tubuh yang besar dan berotot dengan bulu semi-panjang yang lembut dan halus, biasanya dengan pola warna pointed yang khas seperti pada kucing Siam. Mata biru mereka yang besar menambah daya tariknya. Ragdoll memiliki sifat yang sangat ramah dan sosial, sering kali mengikuti pemilik mereka di sekitar rumah dan menikmati waktu bermain serta interaksi. Mereka cenderung rukun dengan anak-anak dan hewan peliharaan lainnya, menjadikannya pilihan ideal untuk keluarga. Meskipun membutuhkan perawatan bulu secara teratur, Ragdoll dikenal sebagai kucing yang mudah diatur dan senang berada di dekat manusia.'],
    ['Kucing Russian Blue adalah ras kucing yang terkenal karena mantel bulunya yang berwarna biru keabu-abuan dengan kilau perak yang khas dan mata hijau besar yang menawan. Mereka memiliki tubuh yang ramping, elegan, dan berotot, dengan telinga yang kecil dan berbentuk segitiga. Kucing Russian Blue dikenal sebagai kucing yang tenang, cerdas, dan sensitif, sering kali membentuk ikatan yang kuat dengan satu atau beberapa anggota keluarga dan cenderung sedikit reserse terhadap orang asing. Mereka suka rutinitas yang konsisten dan lingkungan yang tenang, sehingga cocok untuk pemilik yang tenang dan pengaturan rumah yang stabil. Selain itu, Russian Blue cenderung kurang mengalami masalah kesehatan genetik dibandingkan dengan beberapa ras kucing lainnya, menjadikannya pilihan yang relatif mudah dalam perawatan dan perhatian medis.'],
    ['Kucing Siamese adalah salah satu ras kucing yang paling terkenal dan dihormati di dunia, dikenal dengan tubuh yang ramping, anggun, dan pola warna pointed yang khas dengan tubuh lebih gelap dan ekor, telinga, wajah, dan kaki yang lebih terang. Mata mereka besar, biru, dan bersinar dengan ekspresi yang intens. Kucing Siamese terkenal akan sifatnya yang cerdas, energik, dan vokal, sering kali menggunakan suara mereka untuk berkomunikasi dengan pemiliknya. Mereka sangat sosial dan memerlukan interaksi manusia yang intens, cenderung mencari perhatian dan ikut serta dalam aktivitas rumah tangga. Selain itu, Siamese juga dikenal sebagai kucing yang bersahabat dengan anak-anak dan hewan peliharaan lainnya, menjadikannya pilihan yang cocok untuk keluarga yang aktif dan penuh kasih.'],
    ['Kucing Sphynx adalah salah satu ras kucing yang paling unik, terkenal dengan kurangnya bulu atau memiliki bulu yang sangat tipis sehingga hampir tidak terlihat. Kulit mereka yang halus dan keriput memberi mereka penampilan yang eksotis dan menarik perhatian. Meskipun tidak memiliki bulu untuk melindungi mereka, kucing Sphynx sebenarnya memiliki lapisan minyak alami yang melindungi kulit mereka dan membuat mereka merasa hangat. Mereka memiliki tubuh yang atletis, berotot, dan anggun, serta telinga yang besar dan mata yang menonjol. Kucing Sphynx adalah kucing yang sangat sosial, cerdas, dan penuh energi, sering kali suka mendapatkan perhatian dan bermain dengan pemiliknya. Mereka juga dikenal sebagai kucing yang vokal, menggunakan suara mereka untuk berkomunikasi dengan manusia. Selain itu, kucing Sphynx juga sangat bersahabat dengan anak-anak dan hewan peliharaan lainnya, menjadikannya pilihan yang populer untuk keluarga yang aktif dan penuh kasih. Karena tidak memiliki bulu yang perlu disikat, Sphynx membutuhkan perawatan yang sedikit berbeda seperti menjaga kebersihan kulit dan memastikan suhu ruangan tetap hangat untuk mereka.']
]
PET_CLASSES =  {
            0: ['Abyssinian', PET_FACTS[0]],
            1: ['Bengal', PET_FACTS[1]],
            2: ['Birman', PET_FACTS[2]],
            3: ['Bombay', PET_FACTS[3]],
            4: ['British Shorthair', PET_FACTS[4]],
            5: ['Egyptian Mau', PET_FACTS[5]],
            6: ['Maine Coon', PET_FACTS[6]],
            7: ['Persian', PET_FACTS[7]],
            8: ['Ragdoll',PET_FACTS[8]],
            9: ['Russian Blue',PET_FACTS[9]],
            10: ['Siamese',PET_FACTS[10]],
            11: ['Sphynx', PET_FACTS[11]]
        }

SAVED_COUNTER = './saved_img_amount.txt'

# Membaca isi file dan menyimpan ke variabel global INCREMENT
def load_increment():
    global INCREMENT
    try:
        with open(SAVED_COUNTER, 'r') as file:
            INCREMENT = int(file.read().strip())
    except FileNotFoundError:
        INCREMENT = 0  # Jika file tidak ditemukan, mulai dari 0
    except ValueError:
        INCREMENT = 0  # Jika isi file tidak bisa di-convert ke integer, mulai dari 0


class PetClassifier(Resource):
    def __init__(self):
        self.model = MODEL
        self.pet_classes = PET_CLASSES
        self.increment = 0
        # Load model and classes

    def preprocess_image(self, img):
        
        x = img.size[0]
        y = img.size[1]
        # ratio = 1:1.25
        ratio = 1.15
        if(x < y):
            width = x
            length = int(x * ratio)
            if (length >= y):
                length = y
            # crop it from center with width and length new
            left = 0
            right = x
            top = int((y - length) / 2)
            bottom = int((y + length) / 2)
            img = img.crop((left, top, right, bottom))
        else:
            width = int(y / ratio)
            length = y
            if (width >= x):
                width = x
            # crop it from center with width and length new
            left = int((x - width) / 2)
            right = int((x + width) / 2)
            top = 0
            bottom = y
            img = img.crop((left, top, right, bottom))
               
        img = img.convert('L')  # Convert to grayscale
        img = img.resize((IMG_HEIGHT, IMG_WIDTH))  # Resize to model's input shape
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)  # Expand dims to create batch
        img_array = img_array / 255.0  # Normalize to [0,1]
        return img_array

    def post(self):
        if 'image' not in request.files:
            response = {'pet': 'Error', 'message': 'Gambar Tidak Ditemukan.'}
            return response

        file = request.files['image']

        if file.filename == '':
            response = {'pet': 'Error', 'message': 'Tolong Ambil Foto Kembali.'}
            return response

        # Print file name
        print('Received file:', file.filename)

        if file and file.filename.endswith(('.jpg', '.jpeg', '.png')):
            img = Image.open(io.BytesIO(file.read()))
            # convert into jpg 
            processed_img = self.preprocess_image(img)

            # save image
            global INCREMENT
            
            img.save(f'store_image/img_{INCREMENT}.jpg')
            INCREMENT += 1
            with open(SAVED_COUNTER, 'w') as file:
                file.write(str(INCREMENT))
            
            # Make predictions
            predictions = self.model.predict(processed_img)
            predicted_class = np.argmax(predictions, axis=1)
            predicted_pet = self.pet_classes[predicted_class[0]][0]
            # cek jika level confidence dibawah 50%, maka return {'pet': 'Error', 'message': 'Not sure what pet this is.'}
            if predictions[0][predicted_class[0]] < 0.6:
                response = {'pet': 'Error', 'message': 'Tidak yakin kucing apa ini?'}
                return response
            message = self.pet_classes[predicted_class[0]][1]
            response = {'pet': predicted_pet, 'message': message[0]}
            return response
        else:
            response = {'pet': 'Error', 'message': 'Tolong Ambil Foto Kembali'}
            return response

# Add resource to the API
api.add_resource(PetClassifier, "/kelas")

if __name__ == '__main__':
    load_increment()
    print('Starting server...')
    app.run(debug=True, port=8080)


