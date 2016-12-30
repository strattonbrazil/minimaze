/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.strattonbrazil.minimaze;

import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.files.FileHandle;
import org.python.util.PythonInterpreter;

/**
 *
 * @author stratton
 */
public class PythonUtil {
    static PythonInterpreter getPythonInterpreter() {
        
        if (_interp == null) {
            _interp = new PythonInterpreter();
            
            // TODO: copy all files in python instead of hard-coding
            String[] files = { "maze.py", "minigame.py" };
            FileHandle tmpDir = FileHandle.tempDirectory("py_stuff");
            for (String fileName : files) {
                FileHandle assetPyHandle = Gdx.files.internal("python/" + fileName);
                assetPyHandle.copyTo(tmpDir);
            }
            
            _interp.exec("import sys");
            _interp.exec("sys.path.append('" + tmpDir.path() + "')");
        }

        
        return _interp;
    }
    
    private static PythonInterpreter _interp = null;
}
