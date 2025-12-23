package com.example.snake_control_app;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.constraintlayout.widget.ConstraintLayout;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity extends AppCompatActivity {

    private Button buttonNewGame;
    private Button buttonPause;
    private ConstraintLayout controlsContainer;
    private boolean isGameStarted = false;
    private boolean isGamePaused = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);

        // Инициализация кнопок и контейнера
        buttonNewGame = findViewById(R.id.button_new_game);
        buttonPause = findViewById(R.id.button_pause);
        controlsContainer = findViewById(R.id.controls_container);

        // Настройка слушателя для кнопки НОВАЯ ИГРА/ЗАКОНЧИТЬ
        buttonNewGame.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (!isGameStarted) {
                    startGame();
                } else {
                    endGame();
                }
            }
        });

        // Настройка слушателя для кнопки ПАУЗА/ПРОДОЛЖИТЬ
        buttonPause.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                togglePause();
            }
        });

        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });
    }

    private void startGame() {
        isGameStarted = true;
        isGamePaused = false;

        buttonNewGame.setText("ЗАКОНЧИТЬ");

        buttonPause.setVisibility(View.VISIBLE);
        controlsContainer.setVisibility(View.VISIBLE);
        buttonPause.setText("ПАУЗА");

        ConstraintLayout.LayoutParams params = (ConstraintLayout.LayoutParams) buttonNewGame.getLayoutParams();
        params.topToTop = ConstraintLayout.LayoutParams.PARENT_ID;
        params.bottomToBottom = ConstraintLayout.LayoutParams.UNSET;
        params.topMargin = 100;
        buttonNewGame.setLayoutParams(params);
    }

    private void endGame() {
        isGameStarted = false;
        isGamePaused = false;

        buttonNewGame.setText("НОВАЯ ИГРА");

        buttonPause.setVisibility(View.GONE);
        controlsContainer.setVisibility(View.GONE);

        ConstraintLayout.LayoutParams params = (ConstraintLayout.LayoutParams) buttonNewGame.getLayoutParams();
        params.topToTop = ConstraintLayout.LayoutParams.PARENT_ID;
        params.bottomToBottom = ConstraintLayout.LayoutParams.PARENT_ID;
        params.topMargin = 0;
        buttonNewGame.setLayoutParams(params);
    }

    private void togglePause() {
        if (isGameStarted) {
            isGamePaused = !isGamePaused;

            if (isGamePaused) {
                buttonPause.setText("ПРОДОЛЖИТЬ");
                controlsContainer.setVisibility(View.GONE);
            } else {
                buttonPause.setText("ПАУЗА");
                controlsContainer.setVisibility(View.VISIBLE);
            }
        }
    }
}