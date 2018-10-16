package com.sriyanksiddhartha.speechtotext;

import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.speech.RecognizerIntent;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;

import java.util.ArrayList;
import java.util.Locale;

public class MainActivity extends AppCompatActivity {

	private TextView txvResult, httpResponse;
    EditText ipInput, portInput;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);
		txvResult = (TextView) findViewById(R.id.txvResult);

        ipInput  = (EditText) findViewById(R.id.ipInput);
        portInput  = (EditText) findViewById(R.id.portInput);

        httpResponse = (TextView) findViewById(R.id.httpResponse);

	}

	public void getSpeechInput(View view) {

		Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
		intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
		intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault());

		if (intent.resolveActivity(getPackageManager()) != null) {
			startActivityForResult(intent, 10);
		} else {
			Toast.makeText(this, "Your Device Don't Support Speech Input", Toast.LENGTH_SHORT).show();
		}
	}

	@Override
	protected void onActivityResult(int requestCode, int resultCode, Intent data) {

		super.onActivityResult(requestCode, resultCode, data);

		switch (requestCode) {
			case 10:
				if (resultCode == RESULT_OK && data != null) {
					ArrayList<String> result = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
					txvResult.setText(result.get(0));

					String ipString = ipInput.getText().toString();
                    String portString = portInput.getText().toString();

                    RequestQueue queue = Volley.newRequestQueue(this);
//                    String url ="http://74.64.214.70:9000/" + result.get(0);
                    String url = "http://" + ipString + ':' + portString + '/' + result.get(0);

                    // Request a string response from the provided URL.
                    StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                            new Response.Listener<String>() {
                                @Override
                                public void onResponse(String response) {
                                    // Display the first 500 characters of the response string.
                                    httpResponse.setText("Response: " + response);//+ response.substring(0,500));
                                }
                            }, new Response.ErrorListener() {
                        @Override
                        public void onErrorResponse(VolleyError error) {
							httpResponse.setText("Response Error!");
                        }
                    });
                    // Add the request to the RequestQueue.
                    queue.add(stringRequest);

				}
				break;
		}
	}

}
