package com.example.silksongcontroller

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.activity.enableEdgeToEdge
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat

// MainActivity now implements SensorEventListener to listen to sensor data. [1]
class MainActivity : AppCompatActivity(), SensorEventListener {

    // Declare variables for the sensor system.
    private lateinit var sensorManager: SensorManager
    private var accelerometer: Sensor? = null

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

        // Initialize the SensorManager and get the accelerometer. [2]
        sensorManager = getSystemService(Context.SENSOR_SERVICE) as SensorManager
        accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)

        // Set a listener that executes code when the controlButton is clicked. [4]
        controlButton.setOnClickListener {
            if (!isStarted) {
                // This block runs when the button is clicked and we are in the "Stopped" state.
                isStarted = true
                controlButton.text = "Stop" // Change button text.
                // Register the sensor listener when the controller starts. [3]
                accelerometer?.also { accel ->
                    sensorManager.registerListener(this, accel, SensorManager.SENSOR_DELAY_GAME)
                }
            } else {
                // This block runs when the button is clicked and we are in the "Started" state.
                isStarted = false
                controlButton.text = "Start" // Change button text.
                // Unregister the listener when the controller stops to save battery. [3]
                sensorManager.unregisterListener(this)
                statusTextView.text = "Status: Disconnected" // Reset status text.
            }
        }
    }

    // This function is called every time the sensor provides a new reading. [4]
    override fun onSensorChanged(event: SensorEvent?) {
        if (event?.sensor?.type == Sensor.TYPE_ACCELEROMETER) {
            val xAxis = event.values[0]
            val yAxis = event.values[1]
            val zAxis = event.values[2]

            // Update the status text view with the raw sensor data.
            // We use String.format to neatly format the floating point numbers.
            statusTextView.text = "Status: Running\n\nX: ${String.format("%.2f", xAxis)}\nY: ${String.format("%.2f", yAxis)}\nZ: ${String.format("%.2f", zAxis)}"
        }
    }

    // This function is called when the sensor's accuracy changes. We don't need it. [4]
    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {
        // Do nothing for this app.
    }

    // It's good practice to unregister the listener when the app is paused. [5]
    override fun onPause() {
        super.onPause()
        if (isStarted) {
            sensorManager.unregisterListener(this)
        }
    }

    // And re-register it when the app resumes, if it was started before. [5]
    override fun onResume() {
        super.onResume()
        if (isStarted) {
            accelerometer?.also { accel ->
                sensorManager.registerListener(this, accel, SensorManager.SENSOR_DELAY_GAME)
            }
        }
    }
}