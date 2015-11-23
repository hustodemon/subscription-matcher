package com.suse.matcher.csv;

import com.suse.matcher.json.JsonSubscription;

import java.text.Format;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.TimeZone;


public class CSVOutputSubscription {

    /** Header for CSV output */
    public static final String [] CSV_HEADER = {"Subscription ID","Part Number","Product Description",
        "System Limit","Matched","Start Date (UTC)","End Date (UTC)"};

    /** The id. */
    public Long id;

    /** The part number. */
    public String partNumber;

    /** The subscription name */
    public String name;

    /** The count. */
    public Integer systemLimit;

    /** The consumed. */
    public Integer matched;

    /** Start Date. */
    public Date startsAt = new Date(Long.MIN_VALUE);

    /** End Date. */
    public Date expiresAt = new Date(Long.MAX_VALUE);

    /** SCC Organization Id. */
    public String sccOrgId;

    /** Provided product IDs */
    public Set<Long> productIds = new HashSet<Long>();

    public CSVOutputSubscription(JsonSubscription s) {
        this.id = s.id;
        this.partNumber = s.partNumber;
        this.name = s.name;
        this.systemLimit = s.systemLimit;
        this.matched = 0;
        this.startsAt = s.startsAt;
        this.expiresAt = s.expiresAt;
        this.sccOrgId = s.sccOrgId;
        this.productIds = s.productIds;
    }

    public void increaseMatchCount(int count) {
        if (matched != null) {
            matched = matched + count;
        }
        else {
            matched = new Integer(count);
        }
    }
    
    public List<String> getCSVRow() {
        List<String> row = new ArrayList<>();
        row.add(String.valueOf(id));
        row.add(partNumber);
        row.add(name);
        row.add(String.valueOf(systemLimit));
        row.add(String.valueOf(matched));
        SimpleDateFormat df = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        df.setTimeZone(TimeZone.getTimeZone("UTC"));
        row.add(df.format(startsAt));
        row.add(df.format(expiresAt));
        return row;
    }
}
