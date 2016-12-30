package com.strattonbrazil.minimaze.desktop;

import com.badlogic.gdx.backends.lwjgl.LwjglApplication;
import com.badlogic.gdx.backends.lwjgl.LwjglApplicationConfiguration;
import com.strattonbrazil.minimaze.MinimazeGame;

public class DesktopLauncher {
	public static void main (String[] arg) {
		LwjglApplicationConfiguration config = new LwjglApplicationConfiguration();
                config.width = 1200;
                config.height = 800;
		new LwjglApplication(new MinimazeGame(), config);
	}
}
