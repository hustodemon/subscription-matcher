package com.suse.matcher.model;

import com.google.gson.annotations.SerializedName;

import org.apache.commons.lang3.builder.CompareToBuilder;
import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;

/**
 * Represents match of a subscription to a system requested by the user.
 */
public class Match implements Comparable<Match> {

    /**
     * Kind of this match
     */
    public enum Kind {
        /** Rule engine established that this match can be used */
        POSSIBLE,

        /** Rule engine established it will be part of the result */
        CONFIRMED,

        /** User wants this match, rule engine did not yet confirm it is valid */
        USER_PINNED,

        /** User wanted this match but rule engine denies it's OK to use */
        INVALID
    }

    /** The system id. */
    @SerializedName("system_id")
    public Long systemId;

    /** The subscription id. */
    @SerializedName("subscription_id")
    public Long subscriptionId;

    /** The number of subscriptions used in this match. */
    public Integer quantity;

    /** The kind. */
    public Kind kind;

    /**
     * Standard constructor.
     *
     * @param systemIdIn a system id
     * @param subscriptionIdIn an id of subscription assigned to the system
     * @param quantityIn the number of subscriptions used in this match
     * @param kindIn the match kind
     */
    public Match(Long systemIdIn, Long subscriptionIdIn, Integer quantityIn, Kind kindIn) {
        super();
        systemId = systemIdIn;
        subscriptionId = subscriptionIdIn;
        kind = kindIn;
        quantity = quantityIn;
    }

    /**
     * Gets the system id.
     *
     * @return the system id
     */
    public Long getSystemId() {
        return systemId;
    }

    /**
     * Gets the quantity.
     *
     * @return the quantity
     */
    public Integer getQuantity() {
        return quantity;
    }

    /**
     * Gets the kind.
     *
     * @return the kind
     */
    public Kind getKind() {
        return kind;
    }

    /**
     * Gets the subscription id.
     *
     * @return the subscription id
     */
    public Long getSubscriptionId() {
        return subscriptionId;
    }

    /** {@inheritDoc} */
    @Override
    public int compareTo(Match oIn) {
        return CompareToBuilder.reflectionCompare(this, oIn);
    }

    /** {@inheritDoc} */
    @Override
    public int hashCode() {
        return HashCodeBuilder.reflectionHashCode(this);
    }

    /** {@inheritDoc} */
    @Override
    public boolean equals(Object objIn) {
        return EqualsBuilder.reflectionEquals(this, objIn);
    }

    /** {@inheritDoc} */
    @Override
    public String toString() {
        return ToStringBuilder.reflectionToString(this, ToStringStyle.SHORT_PREFIX_STYLE);
    }
}
