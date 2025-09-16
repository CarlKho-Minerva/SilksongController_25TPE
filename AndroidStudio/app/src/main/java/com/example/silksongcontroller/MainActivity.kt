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
    private var linearAccelerometer: Sensor? = null
    private var gravitySensor: Sensor? = null
    private var isStarted = false

    // Store the latest sensor data for display
    private var accelData = FloatArray(3)
    private var gyroData = FloatArray(3)
    private var linearAccelData = FloatArray(3)
    private var gravityData = FloatArray(3)

    // Dashboard state variables
    private var currentState = "IDLE"
    private var facingDirection = "RIGHT"
    private var rotationDegrees = 0.0f
    private var lastAction = "NONE"
    private var lastActionValue = 0.0f

    // --- Networking and Coroutine Variables ---
    private val coroutineScope = CoroutineScope(Dispatchers.IO) // Scope for background tasks. [1]
    private var udpSocket: DatagramSocket? = null
    private var targetAddress: InetAddress? = null
    private val TARGET_PORT = 12345 // The port our Python script will listen on.

    // --- Throttling Variables ---
    private var lastSendTime: Long = 0
    private val sendIntervalMs: Long = 30 // Send data roughly 33 times a second.

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
        linearAccelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION)
        gravitySensor = sensorManager.getDefaultSensor(Sensor.TYPE_GRAVITY)

        // Set a listener that executes code when the controlButton is clicked. [4]
        controlButton.setOnClickListener {
            if (!isStarted) {
                val ipAddressStr = ipAddressEditText.text.toString()
                if (ipAddressStr.isBlank()) {
                    statusTextView.text = getString(R.string.enter_ip_message)
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
                runOnUiThread { // UI updates must happen on the main thread.
                    controlButton.text = getString(R.string.stop_button)
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
                linearAccelerometer?.also { linearAccel ->
                    sensorManager.registerListener(this@MainActivity, linearAccel, SensorManager.SENSOR_DELAY_GAME)
                    Log.d("UDP", "Linear Accelerometer listener registered")
                }
                gravitySensor?.also { gravity ->
                    sensorManager.registerListener(this@MainActivity, gravity, SensorManager.SENSOR_DELAY_GAME)
                    Log.d("UDP", "Gravity sensor listener registered")
                }
            } catch (e: Exception) {
                e.printStackTrace()
                Log.e("UDP", "Error starting controller: ${e.message}")
                runOnUiThread { statusTextView.text = getString(R.string.network_error_message) }
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
            controlButton.text = getString(R.string.start_button)
            statusTextView.text = getString(R.string.disconnected_status)
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
                // Store accelerometer data for display
                System.arraycopy(event.values, 0, accelData, 0, 3)

                val currentTime = System.currentTimeMillis()
                if ((currentTime - lastSendTime) > sendIntervalMs) { // Throttling check.
                    lastSendTime = currentTime

                    // NEW COMPREHENSIVE MESSAGE FORMAT with all sensor data
                    val message = "SENSOR:" +
                            "${String.format(Locale.US, "%.3f", accelData[0])},${String.format(Locale.US, "%.3f", accelData[1])},${String.format(Locale.US, "%.3f", accelData[2])}," +
                            "${String.format(Locale.US, "%.3f", gyroData[0])},${String.format(Locale.US, "%.3f", gyroData[1])},${String.format(Locale.US, "%.3f", gyroData[2])}," +
                            "${String.format(Locale.US, "%.3f", linearAccelData[0])},${String.format(Locale.US, "%.3f", linearAccelData[1])},${String.format(Locale.US, "%.3f", linearAccelData[2])}," +
                            "${String.format(Locale.US, "%.3f", gravityData[0])},${String.format(Locale.US, "%.3f", gravityData[1])},${String.format(Locale.US, "%.3f", gravityData[2])}"

                    // Send the message in a new background task.
                    coroutineScope.launch {
                        sendUdpMessage(message)
                    }

                    runOnUiThread {
                        updateDashboard()
                    }
                }
            }
            Sensor.TYPE_GYROSCOPE -> {
                // Store the latest gyroscope data (all 3 axes)
                System.arraycopy(event.values, 0, gyroData, 0, 3)
            }
            Sensor.TYPE_LINEAR_ACCELERATION -> {
                // Store the latest linear acceleration data
                System.arraycopy(event.values, 0, linearAccelData, 0, 3)
            }
            Sensor.TYPE_GRAVITY -> {
                // Store the latest gravity data
                System.arraycopy(event.values, 0, gravityData, 0, 3)
            }
        }
    }

    private fun updateDashboard() {
        // Determine state based on accelerometer (similar to Python logic with stability buffer)
        val rawState = when {
            kotlin.math.abs(accelData[1]) > 9.0f -> "COMBAT"
            kotlin.math.abs(accelData[0]) > 9.0f -> "WALKING"
            else -> "IDLE"
        }
        
        // Simple state tracking for display (similar to Python but simplified for Android)
        currentState = rawState

        // Calculate facing direction and rotation from gyro data (similar to Python logic)
        val totalRotation = gyroData[1] // Simplified - in real app this would accumulate over time
        facingDirection = if (totalRotation < 1.57f) "RIGHT" else "LEFT"
        rotationDegrees = Math.toDegrees(totalRotation.toDouble()).toFloat()

        // Calculate jerk force for more accurate action detection (similar to Python)
        val magnitude = kotlin.math.sqrt(accelData[0]*accelData[0] + accelData[1]*accelData[1] + accelData[2]*accelData[2])
        val jerkForce = magnitude - 9.81f
        
        // Enhanced airborne detection (matching Python logic)
        val isAirborne = magnitude in 8.5f..11.5f
        val airborneStatus = if (isAirborne) "AIRBORNE" else "GROUNDED"
        
        // Update last action based on jerk force and enhanced detection
        when (currentState) {
            "COMBAT" -> {
                if (jerkForce > 10.0f) { // Using default punch threshold
                    lastAction = "PUNCH"
                    lastActionValue = jerkForce
                }
            }
            "WALKING" -> {
                if (kotlin.math.abs(accelData[2]) > 3.0f) { // Walking swing detected
                    lastAction = "WALK_SWING"
                    lastActionValue = kotlin.math.abs(accelData[2])
                }
                if (jerkForce > 12.0f) { // Jump threshold
                    lastAction = if (isAirborne) "JUMP_AIRBORNE" else "JUMP_START"
                    lastActionValue = jerkForce
                }
            }
        }

        // Create comprehensive dashboard display matching console format
        val dashboardText = """
══════════════════════════════════════════════
 SILKSONG CONTROLLER DASHBOARD - LIVE DATA
══════════════════════════════════════════════

STATE: $currentState | FACING: $facingDirection (${String.format("%.0f", rotationDegrees)}°)
LAST ACTION: $lastAction (${String.format("%.1f", lastActionValue)})
AIRBORNE STATUS: $airborneStatus

──────────────────────────────────────────────
📱 RAW SENSOR DATA (All Axes):
──────────────────────────────────────────────

🎯 ACCELEROMETER (Motion + Gravity):
   X: ${String.format("%7.2f", accelData[0])} m/s² (Forward/Back)
   Y: ${String.format("%7.2f", accelData[1])} m/s² (Left/Right) 
   Z: ${String.format("%7.2f", accelData[2])} m/s² (Up/Down)

🔄 GYROSCOPE (Rotation Rate):
   X: ${String.format("%7.3f", gyroData[0])} rad/s (Pitch)
   Y: ${String.format("%7.3f", gyroData[1])} rad/s (Yaw)
   Z: ${String.format("%7.3f", gyroData[2])} rad/s (Roll)

🎯 LINEAR ACCELERATION (Pure Motion):
   X: ${String.format("%7.2f", linearAccelData[0])} m/s² 
   Y: ${String.format("%7.2f", linearAccelData[1])} m/s²
   Z: ${String.format("%7.2f", linearAccelData[2])} m/s²

🌍 GRAVITY (Earth's Pull):
   X: ${String.format("%7.2f", gravityData[0])} m/s²
   Y: ${String.format("%7.2f", gravityData[1])} m/s²
   Z: ${String.format("%7.2f", gravityData[2])} m/s²

──────────────────────────────────────────────
📊 COMPUTED VALUES:
──────────────────────────────────────────────
Total Magnitude: ${String.format("%.2f", magnitude)} m/s²
Jerk Force: ${String.format("%.2f", jerkForce)} m/s²
Airborne Range: 8.5 - 11.5 m/s² (Current: ${String.format("%.2f", magnitude)})
══════════════════════════════════════════════
        """.trimIndent()

        statusTextView.text = dashboardText
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