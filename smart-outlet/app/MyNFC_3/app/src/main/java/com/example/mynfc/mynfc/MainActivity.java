package com.example.mynfc.mynfc;

import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.nfc.NfcAdapter;
import android.nfc.Tag;
import android.speech.RecognizerIntent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;


public class MainActivity extends AppCompatActivity {

    //private TextView httpResponse;
    //EditText ipInput, portInput;
    EditText userCode;
    private TextView relayState, timeUsed, powerLeft, serverMessage;

    NfcAdapter nfcAdapter;
    PendingIntent pendingIntent;
    IntentFilter writeTagFilters[];
    boolean writeMode;
    Tag myTag;
    Context context;
    String realy_state = "off";

    TextView nfc_id;
    String card_id = "";
    TextView message;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        context = this;

        //ipInput  = (EditText) findViewById(R.id.ipInput);
        //portInput  = (EditText) findViewById(R.id.portInput);

        userCode  = (EditText) findViewById(R.id.userCode);

        //httpResponse = (TextView) findViewById(R.id.httpResponse);
        relayState = (TextView) findViewById(R.id.relayState);
        timeUsed = (TextView) findViewById(R.id.timeUsed);
        powerLeft = (TextView) findViewById(R.id.powerLeft);
        serverMessage = (TextView) findViewById(R.id.serverMessage);

        nfc_id = (TextView) findViewById(R.id.nfc_id);

        nfc_id.setText("Tap NFC card with phone");

        nfcAdapter = NfcAdapter.getDefaultAdapter(this);
        if (nfcAdapter == null) {
            // Stop here, we definitely need NFC
            Toast.makeText(this, "This device doesn't support NFC.", Toast.LENGTH_LONG).show();
            finish();
        }

        pendingIntent = PendingIntent.getActivity(this, 0, new Intent(this, getClass()).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP), 0);
        IntentFilter tagDetected = new IntentFilter(NfcAdapter.ACTION_TAG_DISCOVERED);
        tagDetected.addCategory(Intent.CATEGORY_DEFAULT);
        writeTagFilters = new IntentFilter[] { tagDetected };
    }

    public void getInfo(View view) {

        //String ipString = ipInput.getText().toString();
        //String portString = portInput.getText().toString();
        String userCodeString = userCode.getText().toString();
        //String tagIdString = nfc_id.getText().toString();
        String tagIdString = card_id;

        RequestQueue queue = Volley.newRequestQueue(this);
//        if (ipString.isEmpty() || portString.isEmpty()){
//            ipString = "ec2-54-86-19-170.compute-1.amazonaws.com";
//            portString = "8080";
//        }
        String ipString = "ec2-54-86-19-170.compute-1.amazonaws.com";
        String portString = "8080";
        String url = "http://" + ipString + ':' + portString + '/' + "info?user_code=" + userCodeString + "&card_id=" + tagIdString;


        // Request a string response from the provided URL.
        StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        // Display the first 500 characters of the response string.
                        //httpResponse.setText("Response: " + response);//+ response.substring(0,500));
                        try {
                            JSONObject jsonResponse = new JSONObject(response);
                            relayState.setText("The relay is " + jsonResponse.getString("relay_state"));
                            timeUsed.setText("Time used: " + jsonResponse.getString("time_used"));
                            powerLeft.setText("Power left: " + jsonResponse.getString("power_left"));
                            if(card_id.isEmpty()){ nfc_id.setText("No NFC card");}
                            else{nfc_id.setText("NFC card paired");}
                            serverMessage.setText(jsonResponse.getString("server_message"));
                            if (jsonResponse.getString("relay_state").equals("on"))
                            {
                                realy_state = "on";
                            }
                            else{
                                realy_state = "off";
                            }
                        }
                        catch  (JSONException e) {

                        }
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                //httpResponse.setText("Response Error!");
                //httpResponse.setText(error.toString());
            }
        });
        // Add the request to the RequestQueue.
        queue.add(stringRequest);
    }

    public void changeRelay(View view) {

        //String ipString = ipInput.getText().toString();
        //String portString = portInput.getText().toString();
        String userCodeString = userCode.getText().toString();
        //String tagIdString = nfc_id.getText().toString();
        String tagIdString = card_id;
        String url;

        RequestQueue queue = Volley.newRequestQueue(this);
//        if (ipString.isEmpty() || portString.isEmpty()){
//            ipString = "ec2-54-86-19-170.compute-1.amazonaws.com";
//            portString = "8080";
//        }
        String ipString = "ec2-54-86-19-170.compute-1.amazonaws.com";
        String portString = "8080";

        url = "http://" + ipString + ':' + portString + '/' + "info?user_code=" + userCodeString + "&card_id=" + tagIdString;


        // Request a string response from the provided URL.
        StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        // Display the first 500 characters of the response string.
                        //httpResponse.setText("Response: " + response);//+ response.substring(0,500));
                        try {
                            JSONObject jsonResponse = new JSONObject(response);
                            relayState.setText("The relay is " + jsonResponse.getString("relay_state"));
                            timeUsed.setText("Time used: " + jsonResponse.getString("time_used"));
                            powerLeft.setText("Power left: " + jsonResponse.getString("power_left"));
                            if(card_id.isEmpty()){ nfc_id.setText("No NFC card");}
                            else{nfc_id.setText("NFC card paired");}
                            serverMessage.setText(jsonResponse.getString("server_message"));
                            if (jsonResponse.getString("relay_state").equals("on"))
                            {
                                realy_state = "on";
                            }
                            else{
                                realy_state = "off";
                            }
                        }
                        catch  (JSONException e) {

                        }
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                //httpResponse.setText("Response Error!");
                //httpResponse.setText(error.toString());
            }
        });
        // Add the request to the RequestQueue.
        queue.add(stringRequest);

        if (realy_state.equals("on"))
        {
            url = "http://" + ipString + ':' + portString + '/' + "relay?user_code=" + userCodeString + "&card_id=" + tagIdString + "&state=off";
        }
        else{
            url = "http://" + ipString + ':' + portString + '/' + "relay?user_code=" + userCodeString + "&card_id=" + tagIdString + "&state=on";
        }

        // Request a string response from the provided URL.
        stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        // Display the first 500 characters of the response string.
                        //httpResponse.setText("Response: " + response);
                        try {
                            JSONObject jsonResponse = new JSONObject(response);
                            relayState.setText("The relay is " + jsonResponse.getString("relay_state"));
                            timeUsed.setText("Time used: " + jsonResponse.getString("time_used"));
                            powerLeft.setText("Power left: " + jsonResponse.getString("power_left"));
                            serverMessage.setText(jsonResponse.getString("server_message"));
                            if(card_id.isEmpty()){ nfc_id.setText("No NFC card");}
                            else{nfc_id.setText("NFC card paired");}
                            if (jsonResponse.getString("relay_state").equals("on"))
                            {
                                realy_state = "on";
                            }
                            else{
                                realy_state = "off";
                            }
                        }
                        catch  (JSONException e) {

                        }
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                //httpResponse.setText("Response Error!");
            }
        });
        // Add the request to the RequestQueue.
        queue.add(stringRequest);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {

        super.onActivityResult(requestCode, resultCode, data);

        switch (requestCode) {
            case 10:
                if (resultCode == RESULT_OK && data != null) {
                    ArrayList<String> result = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);

                    //String ipString = ipInput.getText().toString();
                    //String portString = portInput.getText().toString();
                    String ipString = "ec2-54-86-19-170.compute-1.amazonaws.com";
                    String portString = "8080";

                    RequestQueue queue = Volley.newRequestQueue(this);
//                    String url ="http://74.64.214.70:9000/" + result.get(0);
                    String url = "http://" + ipString + ':' + portString + '/' + result.get(0);

                    // Request a string response from the provided URL.
                    StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                            new Response.Listener<String>() {
                                @Override
                                public void onResponse(String response) {
                                    // Display the first 500 characters of the response string.
                                    //httpResponse.setText("Response: " + response);//+ response.substring(0,500));
                                }
                            }, new Response.ErrorListener() {
                        @Override
                        public void onErrorResponse(VolleyError error) {
                            //httpResponse.setText("Response Error!");
                        }
                    });
                    // Add the request to the RequestQueue.
                    queue.add(stringRequest);

                }
                break;
        }
    }

    @Override
    protected void onNewIntent(Intent intent) {
        setIntent(intent);
        if(NfcAdapter.ACTION_TAG_DISCOVERED.equals(intent.getAction())){
            myTag = intent.getParcelableExtra(NfcAdapter.EXTRA_TAG);
        }

        String hexdump = new String();
        for (int i = 0; i < myTag.getId().length; i++) {
            String x = Integer.toHexString(((int) myTag.getId()[i] & 0xff));
            if (x.length() == 1) {
                x = '0' + x;
            }
            hexdump += x;
        }
        card_id = hexdump;
        //nfc_id.setText(hexdump);
        if(card_id.isEmpty()){ nfc_id.setText("No NFC card");}
        else{nfc_id.setText("NFC card paired");}
    }

    @Override
    public void onPause(){
        super.onPause();
        WriteModeOff();
    }

    @Override
    public void onResume(){
        super.onResume();
        WriteModeOn();
    }



    /******************************************************************************
     **********************************Enable Write********************************
     ******************************************************************************/
    private void WriteModeOn(){
        writeMode = true;
        nfcAdapter.enableForegroundDispatch(this, pendingIntent, writeTagFilters, null);
    }
    /******************************************************************************
     **********************************Disable Write*******************************
     ******************************************************************************/
    private void WriteModeOff(){
        writeMode = false;
        nfcAdapter.disableForegroundDispatch(this);
    }
}
