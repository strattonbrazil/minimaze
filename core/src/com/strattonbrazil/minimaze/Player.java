package com.strattonbrazil.minimaze;

import com.badlogic.gdx.graphics.GL20;
import com.badlogic.gdx.graphics.OrthographicCamera;
import com.badlogic.gdx.graphics.glutils.ImmediateModeRenderer20;
import com.badlogic.gdx.math.Vector2;

public class Player {
    Vector2 _from;
    Vector2 _to;
    boolean _moving;
    float _transition;
    
    Player() {
        _moving = false;
        _from = new Vector2(0,0);
        _to = new Vector2(0,0);
    }
    
    boolean isMoving() { return _moving; }
    
    void setMove(Vector2 dir) {
        _to = new Vector2(_from.x, _from.y);
        _to.add(dir);
        _transition = 0.0f;
        _moving = true;
    }
    
    void draw(ImmediateModeRenderer20 r, OrthographicCamera camera) {        
        // center player in square
        Vector2 mazePos = mazePos();
        camera.translate(-mazePos.y, -mazePos.x);
        camera.update();
        
        r.begin(camera.combined, GL20.GL_TRIANGLE_FAN);
        
        final float RADIUS = 0.1f;
                
        r.color(0,1,0,1);
        r.vertex(-RADIUS, -RADIUS, 0);
        r.color(0,1,0,1);
        r.vertex(-RADIUS, RADIUS, 0);
        r.color(0,1,0,1);
        r.vertex(RADIUS, RADIUS, 0);
        r.color(0,1,0,1);
        r.vertex(RADIUS, -RADIUS, 0);
        
        r.end();
        
        // move camera back
        camera.translate(mazePos.y, mazePos.x);
        camera.update();
    }
    
    // returns in row/column space
    Vector2 mazePos() {
        // add 0.5 so player centered in cell
        return new Vector2(_from.x * (1 - _transition) + _to.x * _transition,
                           _from.y * (1 - _transition) + _to.y * _transition).add(0.5f, 0.5f);
    }
    
    void update(long elapsed) {
        if (_moving) {
            _transition += .0040f * elapsed;
            if (_transition > 0.99999f) {
                _moving = false;
                _from = _to;
                _transition = 0;
            }
        }
    }
}
