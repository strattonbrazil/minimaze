package com.strattonbrazil.minimaze;

import com.badlogic.gdx.graphics.GL20;
import com.badlogic.gdx.graphics.OrthographicCamera;
import com.badlogic.gdx.graphics.glutils.ImmediateModeRenderer20;
import com.badlogic.gdx.math.Vector2;

public class Goal {
    Vector2 _pos;
    Goal(int row, int column) {
        _pos = new Vector2(row, column);
    }
    
    void draw(ImmediateModeRenderer20 r, OrthographicCamera camera) {        
        // center player in square
        Vector2 mazePos = mazePos();
        camera.translate(-mazePos.y, -mazePos.x);
        camera.update();
        
        r.begin(camera.combined, GL20.GL_TRIANGLE_FAN);
        
        final float RADIUS = 0.1f;
                
        r.color(0,1,1,1);
        r.vertex(-RADIUS, -RADIUS, 0);
        r.color(0,1,1,1);
        r.vertex(-RADIUS, RADIUS, 0);
        r.color(0,1,1,1);
        r.vertex(RADIUS, RADIUS, 0);
        r.color(0,1,1,1);
        r.vertex(RADIUS, -RADIUS, 0);
        
        r.end();
        
        // move camera back
        camera.translate(mazePos.y, mazePos.x);
        camera.update();
    }
    
    // in row/column space
    Vector2 mazePos() {
        return new Vector2(_pos.x, _pos.y).add(0.5f, 0.5f);
    }
}
