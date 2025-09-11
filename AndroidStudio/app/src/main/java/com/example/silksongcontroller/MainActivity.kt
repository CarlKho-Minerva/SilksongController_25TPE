package com.example.silksongcontroller

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.activity.enableEdgeToEdge
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat

// MainActivity controls the main screen of our app. [1]
class MainActivity : AppCompatActivity() {

    // Declare variables for our UI elements.
    // 'lateinit' means we promise to initialize them before using them.
    private lateinit var ipAddressEditText: EditText
    private lateinit var controlButton: Button
    private lateinit var statusTextView: TextView

    // A variable to track the current state of the controller.
    private var isStarted = false

    // This function is called when the activity is first created. [2]
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        // This line links our Kotlin file to our XML layout file.
        setContentView(R.layout.activity_main)

        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }

        // Initialize our UI element variables by finding them in the layout by their ID. [3]
        ipAddressEditText = findViewById(R.id.ipAddressEditText)
        controlButton = findViewById(R.id.controlButton)
        statusTextView = findViewById(R.id.statusTextView)

        // Set a listener that executes code when the controlButton is clicked. [4]
        controlButton.setOnClickListener {
            if (!isStarted) {
                // This block runs when the button is clicked and we are in the "Stopped" state.
                isStarted = true
                controlButton.text = "Stop" // Change button text.
                statusTextView.text = "Status: Controller Active" // Update status text.
                // We will add sensor and network logic here later.
            } else {
                // This block runs when the button is clicked and we are in the "Started" state.
                isStarted = false
                controlButton.text = "Start" // Change button text.
                statusTextView.text = "Status: Disconnected" // Update status text.
                // We will add code to stop sensors and networking here later.
            }
        }
    }
}