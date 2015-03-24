package com.suse.matcher;

import com.suse.matcher.model.Subscription;
import com.suse.matcher.model.System;

import org.kie.api.KieServices;
import org.kie.api.event.rule.DebugAgendaEventListener;
import org.kie.api.event.rule.DebugRuleRuntimeEventListener;
import org.kie.api.logger.KieRuntimeLogger;
import org.kie.api.runtime.KieContainer;
import org.kie.api.runtime.KieSession;

import java.util.Date;
import java.util.List;

/**
 * Wraps the rule engine.
 */
public class Matcher {

    /** Filename for internal Drools audit log. */
    public static final String LOG_FILENAME = "drools";

    /**
     * Tries to match systems to subscriptions.
     *
     * @param systems the systems
     * @param subscriptions the subscriptions
     */
    public void match(List<System> systems, List<Subscription> subscriptions) {
        // instantiate engine
        KieServices factory = KieServices.Factory.get();
        KieContainer container = factory.getKieClasspathContainer();
        KieSession session = container.newKieSession("ksession-rules");
        KieRuntimeLogger logger = factory.getLoggers().newFileLogger(session, LOG_FILENAME);

        // set up logging
        session.addEventListener(new DebugAgendaEventListener());
        session.addEventListener(new DebugRuleRuntimeEventListener());

        // insert facts
        for (Subscription subscription : subscriptions) {
            /*
             * A rules engine do not like changing facts during execution. To be
             * on the save side, we do not insert subscriptions which are not
             * valid.
             */
            if (subscription.startsAt.before(new Date()) && subscription.expiresAt.after(new Date())) {
                session.insert(subscription);
            }
        }
        for (System system : systems) {
            session.insert(system);
        }

        // start engine
        session.fireAllRules();
        logger.close();
    }
}
