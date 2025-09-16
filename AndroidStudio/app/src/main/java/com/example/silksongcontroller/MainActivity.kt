package com.example.silksongcontroller

import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.WindowManager
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import kotlinx.coroutines.*
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress

class MainActivity : AppCompatActivity(), SensorEventListener {

    // --- All UI Elements ---
    private lateinit var ipAddressEditText: EditText
    private lateinit var controlButton: Button
    private lateinit var statusTextView: TextView

    // --- Sensors and Networking ---
    private lateinit var sensorManager: SensorManager
    private var accelerometer: Sensor? = null
    private var gyroscope: Sensor? = null
    private var linearAccelerometer: Sensor? = null
    private var gravitySensor: Sensor? = null

    // Data storage for each sensor type
    private val accelData = FloatArray(3)
    private val gyroData = FloatArray(3)
    private val linearAccelData = FloatArray(3)
    private val gravityData = FloatArray(3)

    private var isStarted = false
    private val coroutineScope = CoroutineScope(Dispatchers.IO)
    private var udpSocket: DatagramSocket? = null
    private var targetAddress: InetAddress? = null
    private val TARGET_PORT = 12345
    private var lastSendTime: Long = 0
    private val SEND_INTERVAL_MS: Long = 30 // ~33 FPS

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        ipAddressEditText = findViewById(R.id.ipAddressEditText)
        controlButton = findViewById(R.id.controlButton)
        statusTextView = findViewById(R.id.statusTextView)

        // Set initial UI state
        controlButton.text = getString(R.string.start_button)
        statusTextView.text = getString(R.string.status_disconnected)

        sensorManager = getSystemService(SENSOR_SERVICE) as SensorManager
        accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        gyroscope = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)
        linearAccelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION)
        gravitySensor = sensorManager.getDefaultSensor(Sensor.TYPE_GRAVITY)

        controlButton.setOnClickListener {
            if (!isStarted) startController(ipAddressEditText.text.toString())
            else stopController()
        }
    }

    private fun startController(ipStr: String) {
        if (ipStr.isBlank()) {
            statusTextView.text = getString(R.string.enter_ip_message)
            return
        }
        
        isStarted = true
        coroutineScope.launch {
            try {
                targetAddress = InetAddress.getByName(ipStr)
                udpSocket = DatagramSocket()
                runOnUiThread {
                    controlButton.text = getString(R.string.stop_button)
                    statusTextView.text = "Status: Connecting..."
                    window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
                }
                
                // Register all sensors
                sensorManager.registerListener(this@MainActivity, accelerometer, SensorManager.SENSOR_DELAY_GAME)
                sensorManager.registerListener(this@MainActivity, gyroscope, SensorManager.SENSOR_DELAY_GAME)
                sensorManager.registerListener(this@MainActivity, linearAccelerometer, SensorManager.SENSOR_DELAY_GAME)
                sensorManager.registerListener(this@MainActivity, gravitySensor, SensorManager.SENSOR_DELAY_GAME)

                runOnUiThread {
                    statusTextView.text = "Status: Connected\nSending sensor data..."
                }

                // Start the sending loop
                while (isStarted) {
                    sendSensorData()
                    delay(SEND_INTERVAL_MS)
                }
            } catch (e: Exception) {
                runOnUiThread { 
                    statusTextView.text = getString(R.string.network_error_message)
                    stopController() 
                }
            }
        }
    }

    private fun stopController() {
        isStarted = false
        sensorManager.unregisterListener(this)
        coroutineScope.launch { udpSocket?.close() }
        runOnUiThread {
            controlButton.text = getString(R.string.start_button)
            statusTextView.text = getString(R.string.disconnected_status)
            window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        }
    }

    override fun onSensorChanged(event: SensorEvent?) {
        // Just store the latest data from whichever sensor updated
        when (event?.sensor?.type) {
            Sensor.TYPE_ACCELEROMETER -> {
                System.arraycopy(event.values, 0, accelData, 0, 3)
                updateSensorDisplay()
            }
            Sensor.TYPE_GYROSCOPE -> System.arraycopy(event.values, 0, gyroData, 0, 3)
            Sensor.TYPE_LINEAR_ACCELERATION -> System.arraycopy(event.values, 0, linearAccelData, 0, 3)
            Sensor.TYPE_GRAVITY -> System.arraycopy(event.values, 0, gravityData, 0, 3)
        }
    }
    
    private fun updateSensorDisplay() {
        if (isStarted) {
            runOnUiThread {
                val statusText = getString(R.string.running_status_format,
                    String.format("%.2f", accelData[0]),
                    String.format("%.2f", accelData[1]),
                    String.format("%.2f", accelData[2])
                )
                statusTextView.text = statusText
            }
        }
    }

    private fun sendSensorData() {
        // Construct a comprehensive message with all sensor data
        val message = "SENSOR:" +
                "${accelData[0]},${accelData[1]},${accelData[2]}," +
                "${gyroData[0]},${gyroData[1]},${gyroData[2]}," +
                "${linearAccelData[0]},${linearAccelData[1]},${linearAccelData[2]}," +
                "${gravityData[0]},${gravityData[1]},${gravityData[2]}"

        coroutineScope.launch {
            try {
                val buffer = message.toByteArray()
                val packet = DatagramPacket(buffer, buffer.size, targetAddress, TARGET_PORT)
                udpSocket?.send(packet)
            } catch (e: Exception) {
                // If network error occurs, stop the controller
                runOnUiThread {
                    statusTextView.text = "Status: Network error - ${e.message}"
                    stopController()
                }
            }
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

    override fun onPause() {
        super.onPause()
        if (isStarted) stopController()
    }
}