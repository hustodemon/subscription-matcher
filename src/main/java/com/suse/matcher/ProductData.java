package com.suse.matcher;

import com.suse.matcher.json.JsonProduct;
import com.suse.matcher.json.JsonSystem;

import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.collections4.MapUtils;
import org.apache.commons.collections4.Transformer;

import java.io.InputStreamReader;
import java.io.Reader;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Static product data container.
 */
public class ProductData {

    /** Singleton instance. */
    private static ProductData instance = null;

    /** Map from product IDs to friendly names. */
    private Map<Long, String> friendlyNames;

    /** Private constructor, use <code>getInstance()</code> */
    private ProductData() {
    }

    /** Private constructor, use <code>getInstance()</code> */
    private ProductData(Map<Long, String> friendlyNamesIn) {
        friendlyNames = friendlyNamesIn;
    }

    /**
     * Returns an instance of this class.
     *
     * @return an instance
     */
    public static ProductData getInstance() {
        if (instance == null) {
            Map<Long, String> friendlyNames = new HashMap<>();
            try {
                Reader reader = new InputStreamReader(JsonSystem.class.getResourceAsStream("/products.json"));
                List<JsonProduct> products = new JsonIO().loadProducts(reader);
                MapUtils.populateMap(friendlyNames, products,
                    new Transformer<JsonProduct, Long>(){
                        @Override
                        public Long transform(JsonProduct product) {
                            return product.id;
                        }
                    },
                    new Transformer<JsonProduct, String>(){
                        @Override
                        public String transform(JsonProduct product) {
                            return product.friendlyName;
                        }
                    }
               );
            }
            catch (Exception e) {
                // never happens
                e.printStackTrace();
            }
            instance = new ProductData(friendlyNames);
        }
        return instance;
    }

    /**
     * Gets a collection of friendly names from a collection of product ids.
     *
     * @param productIds the product ids
     * @return the friendly names
     */
    public Collection<String> getFriendlyNames(Set<Long> productIds) {
        return CollectionUtils.collect(productIds, new Transformer<Long,String>(){
            @Override
            public String transform(Long id) {
                if (friendlyNames.containsKey(id)) {
                    return friendlyNames.get(id);
                }
                else {
                    return "Unknown id " + id;
                }
            }
        });
    }
}