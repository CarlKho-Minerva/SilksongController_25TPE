package com.example.silksongcontroller

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.view.WindowManager
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.activity.enableEdgeToEdge
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import kotlinx.coroutines.*
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.util.Locale

// MainActivity now implements SensorEventListener to listen to sensor data. [1]
class MainActivity : AppCompatActivity(), SensorEventListener {

    // --- UI and Sensor Variables ---
    private lateinit var ipAddressEditText: EditText
    private lateinit var controlButton: Button
    private lateinit var statusTextView: TextView
    private lateinit var sensorManager: SensorManager
    private var accelerometer: Sensor? = null
    private var gyroscope: Sensor? = null
    private var isStarted = false
    
    // Store the latest gyroscope data
    private var gyroData = FloatArray(3)

    // --- Networking and Coroutine Variables ---
    private val coroutineScope = CoroutineScope(Dispatchers.IO) // Scope for background tasks. [1]
    private var udpSocket: DatagramSocket? = null
    private var targetAddress: InetAddress? = null
    private val TARGET_PORT = 12345 // The port our Python script will listen on.

    // --- Throttling Variables ---
    private var lastSendTime: Long = 0
    private val SEND_INTERVAL_MS: Long = 30 // Send data roughly 33 times a second.

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

        // Initialize the SensorManager and get the accelerometer and gyroscope. [2]
        sensorManager = getSystemService(Context.SENSOR_SERVICE) as SensorManager
        accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        gyroscope = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)

        // Set a listener that executes code when the controlButton is clicked. [4]
        controlButton.setOnClickListener {
            if (!isStarted) {
                val ipAddressStr = ipAddressEditText.text.toString()
                if (ipAddressStr.isBlank()) {
                    statusTextView.text = "Status: Please enter an IP address."
                    return@setOnClickListener
                }
                startController(ipAddressStr) // Start the controller logic.
            } else {
                stopController() // Stop the controller logic.
            }
        }
    }

    private fun startController(ipAddressStr: String) {
        coroutineScope.launch { // Launch a background task. [1]
            try {
                Log.d("UDP", "Attempting to connect to: $ipAddressStr:$TARGET_PORT")
                targetAddress = InetAddress.getByName(ipAddressStr)
                udpSocket = DatagramSocket() // Create the UDP socket. [2]
                isStarted = true
                Log.d("UDP", "UDP socket created successfully")
                runOnUiThread { 
                    controlButton.text = "Stop"
                    ipAddressEditText.isEnabled = false // Disable IP field while running.
                    
                    // ADD THIS LINE: Keep the screen on to prevent phone from sleeping
                    window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
                }
                accelerometer?.also { accel ->
                    sensorManager.registerListener(this@MainActivity, accel, SensorManager.SENSOR_DELAY_GAME)
                    Log.d("UDP", "Accelerometer listener registered")
                }
                gyroscope?.also { gyro ->
                    sensorManager.registerListener(this@MainActivity, gyro, SensorManager.SENSOR_DELAY_GAME)
                    Log.d("UDP", "Gyroscope listener registered")
                }
            } catch (e: Exception) {
                e.printStackTrace()
                Log.e("UDP", "Error starting controller: ${e.message}")
                runOnUiThread { statusTextView.text = "Status: Invalid IP or network error." }
            }
        }
    }

    private fun stopController() {
        isStarted = false
        sensorManager.unregisterListener(this)
        coroutineScope.launch {
            udpSocket?.close() // Close the socket. [2]
            udpSocket = null
        }
        runOnUiThread {
            controlButton.text = "Start"
            statusTextView.text = "Status: Disconnected"
            ipAddressEditText.isEnabled = true
            
            // ADD THIS LINE: Allow the screen to sleep again when stopped
            window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        }
    }

    // This function is called every time the sensor provides a new reading. [4]
    override fun onSensorChanged(event: SensorEvent?) {
        if (!isStarted || event == null) return

        when (event.sensor.type) {
            Sensor.TYPE_ACCELEROMETER -> {
                val currentTime = System.currentTimeMillis()
                if ((currentTime - lastSendTime) > SEND_INTERVAL_MS) { // Throttling check.
                    lastSendTime = currentTime

                    val xAxis = event.values[0]
                    val yAxis = event.values[1]
                    val zAxis = event.values[2]
                    val gyroY = gyroData[1] // Y-axis rotation (yaw)

                    // NEW MESSAGE FORMAT with gyroscope data
                    val message = "SENSOR:${String.format(Locale.US, "%.3f", xAxis)},${String.format(Locale.US, "%.3f", yAxis)},${String.format(Locale.US, "%.3f", zAxis)},${String.format(Locale.US, "%.3f", gyroY)}"

                    // Send the message in a new background task.
                    coroutineScope.launch {
                        sendUdpMessage(message)
                    }

                    runOnUiThread {
                        statusTextView.text = "Status: Running\n\nX: ${String.format(Locale.US, "%.2f", xAxis)}\nY: ${String.format(Locale.US, "%.2f", yAxis)}\nZ: ${String.format(Locale.US, "%.2f", zAxis)}"
                    }
                }
            }
            Sensor.TYPE_GYROSCOPE -> {
                // Store the latest gyroscope data
                System.arraycopy(event.values, 0, gyroData, 0, 3)
            }
        }
    }

    private fun sendUdpMessage(message: String) {
        udpSocket?.let { socket ->
            try {
                val buffer = message.toByteArray()
                val packet = DatagramPacket(buffer, buffer.size, targetAddress, TARGET_PORT)
                socket.send(packet) // Send the data packet. [3]
                Log.d("UDP", "Sent: $message")
            } catch (e: Exception) {
                Log.e("UDP", "Error sending packet: ${e.message}", e)
            }
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
            stopController()
        }
    }

    // And re-register it when the app resumes, if it was started before. [5]
    override fun onResume() {
        super.onResume()
        // The controller will be restarted manually by the user if needed
    }
}