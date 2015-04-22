package com.suse.matcher;

import org.kie.api.KieServices;
import org.kie.api.event.rule.DebugAgendaEventListener;
import org.kie.api.event.rule.DebugRuleRuntimeEventListener;
import org.kie.api.logger.KieRuntimeLogger;
import org.kie.api.runtime.KieContainer;
import org.kie.api.runtime.KieSession;

import java.util.Collection;

/**
 * Facade on the Drools rule engine.
 *
 * Deduces facts based on some base facts and rules defined ksession-rules.xml.
 */
public class Drools {

    /** Filename for internal Drools audit log. */
    public static final String LOG_FILENAME = "drools";

    /** Deduction resulting fact objects. */
    private Collection<? extends Object> result;

    /**
     * Instantiates a Drools instance with the specified base facts.
     * @param baseFacts fact objects
     */
    public Drools(Collection<Object> baseFacts) {
        // read configuration from kmodule.xml and instantiate the engine
        KieServices factory = KieServices.Factory.get();
        KieContainer container = factory.getKieClasspathContainer();
        KieSession session = container.newKieSession("ksession-rules");
        KieRuntimeLogger logger = factory.getLoggers().newFileLogger(session, LOG_FILENAME);

        // set up logging
        session.addEventListener(new DebugAgendaEventListener());
        session.addEventListener(new DebugRuleRuntimeEventListener());

        // insert base facts
        for (Object fact : baseFacts) {
            session.insert(fact);
        }

        // start deduction engine
        session.fireAllRules();

        // collect results
        result = session.getObjects();

        // cleanup
        logger.close();
        session.dispose();
    }

    /**
     * Returns all facts deduced by Drools.
     * @return the deduced facts
     */
    public Collection<? extends Object> getResult() {
        return result;
    }
}
