package com.example.snake_control_app;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.EditText;

import androidx.appcompat.app.AppCompatActivity;
import androidx.constraintlayout.widget.ConstraintLayout;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;

import org.json.JSONException;
import org.json.JSONObject;

public class MainActivity extends AppCompatActivity {

    private Button buttonNewGame;
    private Button buttonPause;
    private TextView textScore;
    private TextView textStatus;
    private EditText textAddress;
    private ConstraintLayout controlsContainer;

    private Socket socket;
    private PrintWriter out;
    private BufferedReader in;
    private Thread networkThread;
    private int serverPort = 5555;

    private Button buttonUp, buttonDown, buttonLeft, buttonRight;

    private boolean isConnected = false;
    private boolean gameActive = false;
    private boolean gamePaused = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        initViews();
        setupClickListeners();
    }

    private void initViews() {
        buttonNewGame = findViewById(R.id.button_new_game);
        buttonPause = findViewById(R.id.button_pause);
        controlsContainer = findViewById(R.id.controls_container);
        buttonUp = findViewById(R.id.button_up);
        buttonDown = findViewById(R.id.button_down);
        buttonLeft = findViewById(R.id.button_left);
        buttonRight = findViewById(R.id.button_right);
        textAddress = findViewById(R.id.editTextText2);

        textScore = new TextView(this);
        textScore.setTextSize(18);
        textScore.setTextColor(getResources().getColor(android.R.color.white));
        textScore.setText("Счет: 0");

        textStatus = new TextView(this);
        textStatus.setTextSize(16);
        textStatus.setTextColor(getResources().getColor(android.R.color.holo_green_light));
        textStatus.setText("Статус: Отключено");

        ConstraintLayout mainLayout = findViewById(R.id.main);
        ConstraintLayout.LayoutParams params = new ConstraintLayout.LayoutParams(
                ConstraintLayout.LayoutParams.WRAP_CONTENT,
                ConstraintLayout.LayoutParams.WRAP_CONTENT
        );
        params.topToTop = ConstraintLayout.LayoutParams.PARENT_ID;
        params.leftToLeft = ConstraintLayout.LayoutParams.PARENT_ID;
        params.topMargin = 20;
        params.leftMargin = 20;
        textScore.setLayoutParams(params);
        mainLayout.addView(textScore);

        params = new ConstraintLayout.LayoutParams(
                ConstraintLayout.LayoutParams.WRAP_CONTENT,
                ConstraintLayout.LayoutParams.WRAP_CONTENT
        );
        params.topToTop = ConstraintLayout.LayoutParams.PARENT_ID;
        params.rightToRight = ConstraintLayout.LayoutParams.PARENT_ID;
        params.topMargin = 20;
        params.rightMargin = 20;
        textStatus.setLayoutParams(params);
        mainLayout.addView(textStatus);
    }

    private void setupClickListeners() {
        buttonNewGame.setOnClickListener(v -> {
            if (!isConnected) {
                connectToServer();
            } else if (!gameActive) {
                startNewGame();
            } else {
                endGame();
            }
        });

        buttonPause.setOnClickListener(v -> togglePause());

        buttonUp.setOnClickListener(v -> sendCommand("UP"));
        buttonDown.setOnClickListener(v -> sendCommand("DOWN"));
        buttonLeft.setOnClickListener(v -> sendCommand("LEFT"));
        buttonRight.setOnClickListener(v -> sendCommand("RIGHT"));
    }

    private void connectToServer() {
        networkThread = new Thread(() -> {
            try {
                socket = new Socket(textAddress.getText().toString(), serverPort);
                out = new PrintWriter(socket.getOutputStream(), true);
                in = new BufferedReader(new InputStreamReader(socket.getInputStream()));

                runOnUiThread(() -> {
                    isConnected = true;
                    textStatus.setText("Статус: Подключено");
                    textStatus.setTextColor(getResources().getColor(android.R.color.holo_green_light));
                    textAddress.setVisibility(View.GONE);
                    buttonNewGame.setText("НОВАЯ ИГРА");
                    Toast.makeText(this, "Подключено к серверу", Toast.LENGTH_SHORT).show();
                });

                // Создание потока для чтения состояния игры
                new Thread(this::readGameState).start();

            } catch (IOException e) {
                runOnUiThread(() -> {
                    Toast.makeText(this, "Ошибка подключения: " + e.getMessage(), Toast.LENGTH_LONG).show();
                    textStatus.setText("Статус: Ошибка подключения");
                    textStatus.setTextColor(getResources().getColor(android.R.color.holo_red_light));
                });
            }
        });
        networkThread.start();
    }

    private void startNewGame() {
        sendCommand("NEW_GAME");
        gameActive = true;
        gamePaused = false;

        runOnUiThread(() -> {
            buttonNewGame.setText("ЗАВЕРШИТЬ");
            buttonPause.setVisibility(View.VISIBLE);
            buttonPause.setText("ПАУЗА");
            controlsContainer.setVisibility(View.VISIBLE);

            ConstraintLayout.LayoutParams params = (ConstraintLayout.LayoutParams) buttonNewGame.getLayoutParams();
            params.topToTop = ConstraintLayout.LayoutParams.PARENT_ID;
            params.bottomToBottom = ConstraintLayout.LayoutParams.UNSET;
            params.topMargin = 100;
            buttonNewGame.setLayoutParams(params);
        });
    }

    private void endGame() {
        sendCommand("END_GAME");
        gameActive = false;
        gamePaused = false;

        runOnUiThread(this::showMainMenu);
    }

    private void togglePause() {
        if (!gameActive) return;

        sendCommand("PAUSE");
        gamePaused = !gamePaused;

        runOnUiThread(() -> {
            if (gamePaused) {
                buttonPause.setText("ПРОДОЛЖИТЬ");
                controlsContainer.setVisibility(View.GONE);
            } else {
                buttonPause.setText("ПАУЗА");
                controlsContainer.setVisibility(View.VISIBLE);
            }
        });
    }

    private void showMainMenu() {
        buttonNewGame.setText("НОВАЯ ИГРА");
        buttonPause.setVisibility(View.GONE);
        controlsContainer.setVisibility(View.GONE);

        ConstraintLayout.LayoutParams params = (ConstraintLayout.LayoutParams) buttonNewGame.getLayoutParams();
        params.topToTop = ConstraintLayout.LayoutParams.PARENT_ID;
        params.bottomToBottom = ConstraintLayout.LayoutParams.PARENT_ID;
        params.topMargin = 0;
        buttonNewGame.setLayoutParams(params);
    }

    private void sendCommand(String command) {
        if (out != null && !out.checkError()) {
            new Thread(() -> {
                out.println(command);
                try {
                    String response = in.readLine();
                    if (response != null && response.equals("OK")) {
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }).start();
        }
    }

    private void readGameState() {
        try {
            String line;
            while ((line = in.readLine()) != null) {
                try {
                    JSONObject gameState = new JSONObject(line);
                    updateUI(gameState);
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
        } catch (IOException e) {
            runOnUiThread(() -> {
                isConnected = false;
                gameActive = false;
                showMainMenu();
                textStatus.setText("Статус: Отключено");
                textStatus.setTextColor(getResources().getColor(android.R.color.holo_red_light));
                Toast.makeText(this, "Соединение разорвано", Toast.LENGTH_SHORT).show();
            });
        }
    }

    private void updateUI(JSONObject gameState) {
        runOnUiThread(() -> {
            try {
                String status = gameState.getString("status");
                int score = gameState.getInt("score");

                textScore.setText("Счет: " + score);

                switch (status) {
                    case "WAITING":
                        textStatus.setText("Статус: Ожидание игры");
                        textStatus.setTextColor(getResources().getColor(android.R.color.darker_gray));
                        break;
                    case "PLAYING":
                        textStatus.setText("Статус: Игра идет");
                        textStatus.setTextColor(getResources().getColor(android.R.color.holo_green_light));
                        break;
                    case "PAUSED":
                        textStatus.setText("Статус: Пауза");
                        textStatus.setTextColor(getResources().getColor(android.R.color.holo_orange_light));
                        break;
                    case "GAME_OVER":
                        textStatus.setText("Статус: Игра окончена");
                        textStatus.setTextColor(getResources().getColor(android.R.color.holo_red_light));

                        if (gameActive) {
                            gameActive = false;
                            showMainMenu();
                            Toast.makeText(this, "Игра окончена! Счет: " + score, Toast.LENGTH_LONG).show();
                        }
                        break;
                }

                if (status.equals("GAME_OVER") && gameActive) {
                    gameActive = false;
                    showMainMenu();
                }

            } catch (JSONException e) {
                e.printStackTrace();
            }
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        disconnectFromServer();
    }

    private void disconnectFromServer() {
        if (networkThread != null && networkThread.isAlive()) {
            networkThread.interrupt();
        }

        try {
            if (out != null) {
                out.close();
            }
            if (in != null) {
                in.close();
            }
            if (socket != null) {
                socket.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}