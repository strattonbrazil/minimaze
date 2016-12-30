package com.strattonbrazil.minimaze;

import com.badlogic.gdx.ApplicationAdapter;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.Input;
import com.badlogic.gdx.graphics.Color;
import com.badlogic.gdx.graphics.GL20;
import com.badlogic.gdx.graphics.OrthographicCamera;
import com.badlogic.gdx.graphics.Pixmap;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.g2d.BitmapFont;
import com.badlogic.gdx.graphics.g2d.SpriteBatch;
import com.badlogic.gdx.graphics.glutils.FrameBuffer;
import com.badlogic.gdx.graphics.glutils.ImmediateModeRenderer20;
import com.badlogic.gdx.math.Vector2;
import com.badlogic.gdx.utils.TimeUtils;
import org.python.util.PythonInterpreter;

public class MinimazeGame extends ApplicationAdapter {
    BitmapFont _font;
    SpriteBatch batch;
    Texture img;
    Player _player;
    Goal _goal;
    Maze _maze;
    Minigame _minigame;
    long _lastTime;
    FrameBuffer _minigameBuffer;
    Vector2 _relativeMinigameCursorPos;
    float _minigameOpacity;
    long _deathStart;

    final int NUM_ROWS = 1;
    final int NUM_COLUMNS = 3;
    
    enum GameMode { SEARCHING, GOAL, FLEEING, DYING };
    
    GameMode _mode;
    
    @Override
    public void create () {
        batch = new SpriteBatch();
        img = new Texture("badlogic.jpg");
        _font = new BitmapFont();
        _font.setColor(Color.RED);
        
        _player = new Player();
        _goal = new Goal(NUM_ROWS-1,NUM_COLUMNS-1);
        _maze = new Maze(NUM_ROWS,NUM_COLUMNS);
        _minigame = new Minigame();
        _relativeMinigameCursorPos = new Vector2(0,0);
        
        PythonInterpreter interp = new PythonInterpreter();
        _lastTime = TimeUtils.millis();
        _mode = GameMode.SEARCHING;
    }

    @Override
    public void render () {
        update();
        
        renderMinigame();
        
        renderMaze();
    }

    private void renderMinigame() {
        if (_minigameBuffer == null) {
            _minigameBuffer = new FrameBuffer(Pixmap.Format.RGBA8888, 512, 512, true);
        }
        _minigameBuffer.begin();
        _minigame.draw();
        _minigameBuffer.end();
    }
    
    private void renderMaze() {
        Gdx.gl.glClearColor(0, 0, 0, 1);
        Gdx.gl.glClear(GL20.GL_COLOR_BUFFER_BIT);
        
        ImmediateModeRenderer20 r = new ImmediateModeRenderer20(false, true, 0);
        
        OrthographicCamera camera = new OrthographicCamera();
        
        final int WIDTH = Gdx.graphics.getWidth();
        final int HEIGHT = Gdx.graphics.getHeight();
        
        final float ASPECT = (float)WIDTH / HEIGHT;
        final float CELL_HEIGHT = NUM_ROWS + 2; // leave cell worth on top and bottom
        final float PIXELS_PER_CELL = HEIGHT / CELL_HEIGHT;
        final float NUM_HORIZONTAL_CELLS = WIDTH / PIXELS_PER_CELL;
        
        camera.setToOrtho(true, ASPECT * CELL_HEIGHT, CELL_HEIGHT);
        camera.translate(-(NUM_HORIZONTAL_CELLS - NUM_COLUMNS) * 0.5f, -1, 0);
        camera.update();
        
        _maze.draw(r, camera);
        _player.draw(r, camera);
        _goal.draw(r, camera);
        
        final float MINIGAME_PADDING = 40;
        final float MINIGAME_RENDER_SIZE = HEIGHT - MINIGAME_PADDING * 2;
        final float MINIGAME_LEFT_OFFSET = (WIDTH - MINIGAME_RENDER_SIZE) * 0.5f;
        
        _relativeMinigameCursorPos = new Vector2((Gdx.input.getX() - MINIGAME_LEFT_OFFSET) / MINIGAME_RENDER_SIZE,
                                                 (Gdx.input.getY() - MINIGAME_PADDING) / MINIGAME_RENDER_SIZE);
        
        if (_mode == GameMode.GOAL) {
            batch.begin();
            batch.setColor(1.0f, 1.0f, 1.0f, _minigameOpacity);
            batch.draw(_minigameBuffer.getColorBufferTexture(), 
                       MINIGAME_LEFT_OFFSET, 
                       MINIGAME_PADDING, 
                       MINIGAME_RENDER_SIZE, MINIGAME_RENDER_SIZE);
            batch.end();
        } else if (_mode == GameMode.DYING) {
            //_font.draw(batch, "Hello World", 200, 200);
        }
    }
    
    @Override
    public void dispose () {
        batch.dispose();
        img.dispose();
    }
    
    private void update() {
        // calculate elapsed time
        final long currentTime = TimeUtils.millis();
        final long elapsed = currentTime - _lastTime;
        _lastTime = currentTime;
        
        // handle player controls
        if (_mode != GameMode.GOAL && _mode != GameMode.DYING && !_player.isMoving()) {
            Vector2 pos = _player.mazePos();
            if (Gdx.input.isKeyPressed(Input.Keys.S) && _maze.hasWall((int)pos.x, (int)pos.y, "down")) {
                _player.setMove(new Vector2(1,0));
            } else if (Gdx.input.isKeyPressed(Input.Keys.W) && _maze.hasWall((int)pos.x, (int)pos.y, "up")) {
                _player.setMove(new Vector2(-1,0));
            } else if (Gdx.input.isKeyPressed(Input.Keys.A) && _maze.hasWall((int)pos.x, (int)pos.y, "left")) {
                _player.setMove(new Vector2(0,-1));
            } else if (Gdx.input.isKeyPressed(Input.Keys.D) && _maze.hasWall((int)pos.x, (int)pos.y, "right")) {
                _player.setMove(new Vector2(0,1));
            }
        }
        
        _player.update(elapsed);
        _minigame.update(elapsed, _relativeMinigameCursorPos);
        
        // entering goal area
        if (_mode == GameMode.SEARCHING && _player.mazePos().dst(_goal.mazePos()) < 0.1f) {
            _mode = GameMode.GOAL;
            _minigameOpacity = 0.0f;
        } else if (_mode == GameMode.GOAL) {
            _minigameOpacity = Math.min(_minigameOpacity + 0.001f * elapsed, 1.0f);
            if (_minigameOpacity > 0.95) {
                _minigame.start();
            }
            
            if (_minigame.isFinished()) {
                if (_minigame.isSuccess())
                    _mode = GameMode.FLEEING;
                else {
                    _mode = GameMode.DYING;
                    _deathStart = TimeUtils.millis();
                }
            }
        }
        
    }
}
