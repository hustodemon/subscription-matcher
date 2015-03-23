package com.suse.matcher;

import com.suse.matcher.model.Subscription;
import com.suse.matcher.model.System;

import java.io.FileReader;
import java.util.List;

/**
 * Entry point for the commandline version of this program.
 */
public class Main {

    /**
     * The main method.
     *
     * @param args commandline arguments
     * @throws Exception if anything unexpected happens
     */
    public static final void main(String[] args) throws Exception {
        // parse commandline
        if (args.length != 2) {
            java.lang.System.err.println("Usage: java -jar matcher.jar systems.json subscriptions.json");
            java.lang.System.exit(1);
        }
        String systemsPath = args[0];
        String subscriptionsPath = args[1];

        // load files
        Loader loader = new Loader();
        List<System> systems = loader.loadSystems(new FileReader(systemsPath));
        List<Subscription> subscriptions = loader.loadSubscriptions(new FileReader(subscriptionsPath));

        // run the engine
        new Matcher().match(systems, subscriptions);

        // print results
        for (System system : systems) {
            for (Subscription subscription : system.applicableSubscriptions) {
                java.lang.System.out.println(subscription.id + " can be used for " + system.id);
            }
        }

        java.lang.System.exit(0);
    }
}
