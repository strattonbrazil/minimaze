package com.strattonbrazil.minimaze;

import com.badlogic.gdx.graphics.GL20;
import com.badlogic.gdx.graphics.OrthographicCamera;
import com.badlogic.gdx.graphics.glutils.ImmediateModeRenderer20;
import com.badlogic.gdx.math.Vector2;
import java.util.HashSet;
import org.python.core.PyObject;
import org.python.util.PythonInterpreter;

public class Maze {
    final int NUM_ROWS;
    final int NUM_COLUMNS;
    HashSet<String> _openWalls;
    Vector2 _playerPosition;
        
    Maze(final int numRows, final int numColumns) {
        NUM_ROWS = numRows;
        NUM_COLUMNS = numColumns;
        
        _openWalls = new HashSet<String>();
        
        PythonInterpreter interp = PythonUtil.getPythonInterpreter();
                
        interp.exec("import maze");
        PyObject openWalls = interp.eval("maze.create_maze(" + NUM_ROWS + "," + NUM_COLUMNS + ")");
        
        for (int i = 0; i < openWalls.__len__(); i++) {
            PyObject wall = openWalls.__getitem__(i);
            final int row = wall.__getitem__(0).asInt();
            final int column = wall.__getitem__(1).asInt();
            final String side = wall.__getitem__(2).asString();
            
            _openWalls.add(wallToKey(row, column, side));
        }
        //interp.execfile("/home/stratton/Public/parts/python/maze.py");
    }
    
    void setPlayerPosition(Vector2 pos) {
        _playerPosition = pos;
    }
        
    String wallToKey(int row, int column, String dir) {
        return String.format("%d_%d_%s", row, column, dir);
    }

    void draw(ImmediateModeRenderer20 r, OrthographicCamera camera) {
        final float PADDING = 0.05f;
        
        r.begin(camera.combined, GL20.GL_LINES);
        
        for (int row = 0; row < NUM_ROWS; row++) {
            for (int column = 0; column < NUM_COLUMNS; column++) {
                Cell cell = getCell(row, column);
                
                if (!cell.up) {
                    r.color(1,0,0,1);
                    r.vertex(column, row + PADDING, 0);
                    r.color(1,0,0,1);
                    r.vertex(column+1, row + PADDING, 0);
                }
                if (!cell.down) {
                    r.color(1,1,1,1);
                    r.vertex(column, row+1 - PADDING, 0);
                    r.color(1,1,1,1);
                    r.vertex(column+1, row+1 - PADDING, 0);
                }
                if (!cell.left) {
                    r.color(0,1,1,1);
                    r.vertex(column + PADDING, row, 0);
                    r.color(0,1,1,1);
                    r.vertex(column + PADDING, row+1, 0);
                }
                if (!cell.right) {
                    r.color(1,0,1,1);
                    r.vertex(column+1 - PADDING, row, 0);
                    r.color(1,0,1,1);
                    r.vertex(column+1 - PADDING, row+1, 0);
                }
            }
        }
        
        r.end();
        
        boolean drawShadows = false;
        if (drawShadows) {
            Vector2 playerSource = new Vector2(_playerPosition.y, _playerPosition.x); // switch to x,y
            for (int row = 0; row < NUM_ROWS; row++) {
                for (int column = 0; column < NUM_COLUMNS; column++) {
                    Cell cell = getCell(row, column);
                    if (!cell.up) {
                        Vector2 a = new Vector2(column, row);
                        Vector2 b = new Vector2(column+1, row);
                        drawExtrudedQuad(camera, r, playerSource, a, b);
                    }
                    if (!cell.down) {
                        Vector2 a = new Vector2(column, row+1);
                        Vector2 b = new Vector2(column+1, row+1);
                        drawExtrudedQuad(camera, r, playerSource, a, b);
                    }
                    if (!cell.left) {
                        Vector2 a = new Vector2(column, row);
                        Vector2 b = new Vector2(column, row+1);
                        drawExtrudedQuad(camera, r, playerSource, a, b);
                    }
                    if (!cell.right) {
                        Vector2 a = new Vector2(column+1, row);
                        Vector2 b = new Vector2(column+1, row+1);
                        drawExtrudedQuad(camera, r, playerSource, a, b);
                    }
                }
            }
        }
    }
    
    void drawExtrudedQuad(OrthographicCamera camera, ImmediateModeRenderer20 r, Vector2 source, Vector2 a, Vector2 b) {
        r.begin(camera.combined, GL20.GL_TRIANGLE_FAN);
        
        Vector2 aV = a.cpy().sub(source).nor().scl(1000).add(a);
        Vector2 bV = b.cpy().sub(source).nor().scl(1000).add(b);
        
        r.color(0,0,0,1);
        r.vertex(a.x, a.y, 0);
        r.color(0,0,0,1);
        r.vertex(aV.x, aV.y, 0);
        r.color(0,0,0,1);
        r.vertex(bV.x, bV.y, 0);
        r.color(0,0,0,1);
        r.vertex(b.x, b.y, 0);
        
        r.end();
    }
    
    Cell getCell(int row, int column) {
        return new Cell(
            _openWalls.contains(wallToKey(row, column-1, "right")),
            _openWalls.contains(wallToKey(row, column, "right")),
            _openWalls.contains(wallToKey(row-1, column, "down")),
            _openWalls.contains(wallToKey(row, column, "down"))
        );
    }
    
    boolean hasWall(int row, int column, String dir) {
        if (dir == "left") {
            dir = "right";
            column -= 1;
        } else if (dir == "up") {
            dir = "down";
            row -= 1;
        }
        
        return _openWalls.contains(wallToKey(row, column, dir));
    }
    
    private class Cell
    {
        final boolean left, right, up, down;
        
        Cell(boolean left, boolean right, boolean up, boolean down) {
            this.left = left;
            this.right = right;
            this.up = up;
            this.down = down;
        }
    }
}
