
package net.runeloader.loader;

import java.util.ServiceLoader;

public class ModLoaderAPI {
    public static void loadMods() {
        ServiceLoader<IModEntry> loader = ServiceLoader.load(IModEntry.class);
        for (IModEntry mod : loader) {
            System.out.println("Loading mod: " + mod.getName());
            mod.onInitialize();
        }
    }
}
