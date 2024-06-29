package com.example.knowyourcat;


import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import android.os.Build;
import android.content.ContentValues;
import android.os.Environment;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.File;
import androidx.activity.EdgeToEdge;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import org.json.JSONObject;
import org.w3c.dom.Text;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;

import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.io.InputStreamReader;

public class MainActivity extends AppCompatActivity {

    private Button buttonTakePhoto;
    private ImageView imageViewPhoto;
    private TextView textViewKelas;

    private TextView textViewPesan;

    private Uri savedFileUri;
    private static final int IMAGE_SIZE = 400;
    private static final int cameraRequestCode = 222;

    private static final String serverURL = "https://83de-180-248-21-200.ngrok-free.app/kelas";


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        this.buttonTakePhoto = (Button) findViewById(R.id.buttonTakePhoto);
        this.imageViewPhoto = (ImageView) findViewById(R.id.imageViewPhoto);
        this.textViewKelas = (TextView) findViewById(R.id.textViewKelas);
        this.textViewPesan = (TextView) findViewById(R.id.textViewPesan);

        this.buttonTakePhoto.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                CharSequence filename  = new SimpleDateFormat("MM-dd-yy hh-mm-ss").format(new Date());
                MainActivity.this.savedFileUri = null;

                if (Build.VERSION.SDK_INT > 28) {
                    ContentValues values = new ContentValues();
                    values.put(MediaStore.Images.Media.DISPLAY_NAME, filename + ".jpeg");
                    values.put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg");
                    values.put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES);
                    MainActivity.this.savedFileUri = getContentResolver().insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values);
                }
                else {
                    File imagesFolder = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DCIM), getString(R.string.app_name));
                    if (!imagesFolder.exists() && !imagesFolder.mkdir()) {
                        Toast.makeText(MainActivity.this, "Error dalam pembuatan folder penyimpanan citra", Toast.LENGTH_SHORT).show();
                        return;
                    }
                    File imageFile = new File(imagesFolder, filename + ".jpeg");
                    MainActivity.this.savedFileUri = Uri.fromFile(imageFile);
                }

                Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
                intent.putExtra(MediaStore.EXTRA_OUTPUT, MainActivity.this.savedFileUri);
                startActivityForResult(intent, cameraRequestCode);
            }
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (resultCode == Activity.RESULT_OK) {
            switch (requestCode) {
                case(cameraRequestCode):
                    ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
                    InputStream inputStream = null;
                    try {
                        inputStream = getContentResolver().openInputStream(MainActivity.this.savedFileUri);
                        Bitmap bitmapgambar = BitmapFactory.decodeStream(inputStream);
                        int maxSize = Math.max(bitmapgambar.getWidth(), bitmapgambar.getHeight());

                        // Bitmap bitmapBaru = Bitmap.createScaledBitmap(bitmapgambar, Math.max(IMAGE_SIZE * bitmapgambar.getWidth() / maxSize, 1), Math.max(IMAGE_SIZE * bitmapgambar.getHeight() / maxSize, 1), false);
                        Bitmap rotatedBitmap = rotateImage(bitmapgambar, 0);
                        imageViewPhoto.setImageBitmap(rotatedBitmap);
                        Bitmap bitmapBaru = Bitmap.createScaledBitmap(rotatedBitmap, Math.max(IMAGE_SIZE * rotatedBitmap.getWidth() / maxSize, 1), Math.max(IMAGE_SIZE * rotatedBitmap.getHeight() / maxSize, 1), false);
                        saveFile(bitmapBaru);
                    }catch (Exception ignore){
                    }finally{
                        try{
                            inputStream.close();
                        }catch (Exception ignore){

                        }

                    }
                    break;
            }
        }
    }
    private Bitmap rotateImage(Bitmap source, float angle) {
        Matrix matrix = new Matrix();
        matrix.postRotate(angle);
        return Bitmap.createBitmap(source, 0, 0, source.getWidth(), source.getHeight(), matrix, true);
    }

    private void saveFile(Bitmap bitmap) {
        Date date = new Date();
        String fileName = new SimpleDateFormat("yyyyMMdd-hh-mm-ss", Locale.US).format(date) + ".png";

        new Thread(() -> {
            HttpURLConnection connection;
            DataOutputStream writer = null;
            ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
            BufferedReader reader = null;
            StringBuilder response = new StringBuilder();
            try {

                bitmap.compress(Bitmap.CompressFormat.PNG, 100, byteArrayOutputStream);
                byte[] imageData = byteArrayOutputStream.toByteArray();

                URL url = new URL(MainActivity.this.serverURL);
                connection = (HttpURLConnection) url.openConnection();
                connection.setRequestMethod("POST");
                connection.setRequestProperty("Content-Type", "multipart/form-data;boundary=*****");
                connection.setRequestProperty("Accept", "application/json");
                connection.setDoOutput(true);

                writer = new DataOutputStream(connection.getOutputStream());
                writer.writeBytes("--*****\r\n");
                writer.writeBytes("Content-Disposition: form-data; name=\"image\";filename=\"" + fileName + "\"\r\n");
                writer.writeBytes("\r\n");
                writer.write(imageData);
                writer.writeBytes("\r\n");
                writer.writeBytes("--*****--\r\n");

                int responseCode = connection.getResponseCode();
                if (responseCode == HttpURLConnection.HTTP_OK) {
                    reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                    String line;
                    while ((line = reader.readLine()) != null) {
                        response.append(line);
                    }
                    JSONObject responseObject = new JSONObject(response.toString());
                    String pet_class = responseObject.getString("pet");
                    String pesan = responseObject.getString("message");
                    runOnUiThread(() -> {
                        textViewKelas.setText(pet_class);
                        textViewPesan.setText(pesan);
                    });
                }else{
                    runOnUiThread(() -> {
                        Toast.makeText(MainActivity.this, "Error upload foto ke server", Toast.LENGTH_SHORT).show();
                    });
                }


            }
            catch (Exception e) {
                e.printStackTrace();
            }finally {
                try {
                    writer.close();
                }
                catch (Exception ignored) {}
            }
        }).start();
    }
}