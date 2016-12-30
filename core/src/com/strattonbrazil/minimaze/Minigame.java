package com.strattonbrazil.minimaze;

import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.Input.Buttons;
import com.badlogic.gdx.audio.Sound;
import com.badlogic.gdx.graphics.GL20;
import com.badlogic.gdx.graphics.OrthographicCamera;
import com.badlogic.gdx.graphics.glutils.ImmediateModeRenderer20;
import com.badlogic.gdx.math.Vector2;
import com.badlogic.gdx.utils.TimeUtils;
import org.python.core.PyObject;
import org.python.core.PyString;
import org.python.util.PythonInterpreter;

public class Minigame {
    private PythonInterpreter _interp;
    private PyObject _gameContext;
    private PyObject _minigame;
    private boolean _started;
    private boolean _leftMouseWasUp;
    private long _startTime;
    private boolean _isFinished;
    private boolean _isSuccess;
            
    Minigame() {
        _interp = PythonUtil.getPythonInterpreter();
        
        _interp.exec("import minigame");
        _gameContext = _interp.eval("{ 'status' : 'starting' }");
        _minigame = _interp.eval("minigame.Minigame()");
        _started = false;
        _leftMouseWasUp = true;
        _isFinished = false;
        _isSuccess = false;
    }
    
    void start() {
        if (!_started) {
            _startTime = TimeUtils.millis();
            _started = true;
        }
    }
    
    void draw() {
        Gdx.gl.glClearColor(0.2f,0.2f,0.2f,1);
        Gdx.gl.glClear(GL20.GL_COLOR_BUFFER_BIT);
        
        ImmediateModeRenderer20 r = new ImmediateModeRenderer20(false, true, 0);
        
        OrthographicCamera camera = new OrthographicCamera();
        camera.setToOrtho(false, 1, 1);
        camera.update();
                
        PyObject assets = _gameContext.__getitem__(new PyString("assets"));
        for (int i = 0; i < assets.__len__(); i++) {
            float[] color = { 1, 1, 1, 1};
            float[] position = { 0, 0, 0 };
            float[] size = { 0, 0 };

            PyObject asset = assets.__getitem__(i);
            if (asset.__getitem__(new PyString("type")).toString() == "rectangle") {
                parseArray(asset.__getitem__(new PyString("color")), color);
                parseArray(asset.__getitem__(new PyString("position")), position);
                parseArray(asset.__getitem__(new PyString("size")), size);
                
                r.begin(camera.combined, GL20.GL_TRIANGLE_FAN);
                r.color(color[0], color[1], color[2], color[3]);
                r.vertex(position[0], position[1], position[2]);
                r.color(color[0], color[1], color[2], color[3]);
                r.vertex(position[0], position[1] + size[1], position[2]);
                r.color(color[0], color[1], color[2], color[3]);
                r.vertex(position[0] + size[0], position[1] + size[1], position[2]);
                r.color(color[0], color[1], color[2], color[3]);
                r.vertex(position[0] + size[0], position[1], position[2]);
                r.end();
            }
        }
    }
    
    void parseArray(PyObject pyArray, float[] array) {
        for (int i = 0; i < pyArray.__len__(); i++) {
            array[i] = (float)pyArray.__getitem__(i).asDouble();
        }
    }
    
    PyObject toPyBool(boolean b) {
        if (b)
            return _interp.eval("True");
        return _interp.eval("False");
    }
    
    void update(final long elapsed, Vector2 relativeCursorPos) {
        _gameContext.__setitem__("elapsed", _interp.eval(Long.toString(elapsed)));
        
        _gameContext.__setitem__("mousePos", _interp.eval("(" + relativeCursorPos.x + "," + relativeCursorPos.y + ")"));
      
        boolean leftMouseDown = Gdx.input.isButtonPressed(Buttons.LEFT);
        _gameContext.__setitem__("mouseDown", toPyBool(leftMouseDown));  
        _gameContext.__setitem__("mousePress", toPyBool(_leftMouseWasUp && leftMouseDown));
        _leftMouseWasUp = !leftMouseDown;

        boolean gameStarting = _gameContext.__getitem__(new PyString("status")).toString() == "starting";
        
        if (_started && gameStarting && TimeUtils.millis() - _startTime > 1000) {
            System.out.println("setting game to play mode");
            _gameContext.__setitem__(new PyString("status"), new PyString("playing"));
            _gameContext.__setitem__(new PyString("startTime"), _interp.eval(Long.toString(TimeUtils.millis())));
        }
        _gameContext.__setitem__(new PyString("currentTime"), _interp.eval(Long.toString(TimeUtils.millis())));
        
        
        String status = _gameContext.__getitem__(new PyString("status")).toString();
        if (status == "success" || status == "failure") {
            _isFinished = true;
            _isSuccess = status == "success";
        }
        
        _minigame.invoke("update", _gameContext);
        
        if (_gameContext.__contains__(new PyString("sound"))) {
            String soundName = _gameContext.__getitem__(new PyString("sound")).asString();
            Sound sound = Gdx.audio.newSound(Gdx.files.internal("sounds/" + soundName + ".wav"));
            sound.play(1.0f);
            _gameContext.__delitem__("sound");
        }
    }
    
    boolean isFinished() {
        return _isFinished;
    }
    
    boolean isSuccess() {
        return _isSuccess;
    }
}
