package com.suse.matcher.facts;

import org.apache.commons.lang3.builder.CompareToBuilder;
import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import org.kie.api.definition.type.PropertyReactive;

/**
 * A PartialMatch is a potential application of a {@link Subscription} to a {@link System}
 * and a {@link Product}.
 *
 * Such a fact is generated if the Subscription-System-Product triple is a legal one on its
 * own, that is, without taking any other PartialMatches into account.
 *
 * PartialMatches can be grouped together. PartialMatches in such groups must either be
 * be all matched or none of them can be matched.
 */
@PropertyReactive
public class PartialMatch implements Comparable<PartialMatch> {

    /** The system id. */
    public long systemId;

    /** The product id. */
    public long productId;

    /** The subscription id. */
    public long subscriptionId;

    /** The id of the cent group used in this match. More matches can share same cent group. */
    public int centGroupId;

    /** The group id. */
    public int groupId;

    /**
     * Standard constructor.
     *
     * @param systemIdIn a system id
     * @param productIdIn an id of a product
     * @param subscriptionIdIn an id of subscription assigned to the system
     * @param centGroupIdIn the id of cent group
     * @param groupIdIn the group id
     */
    public PartialMatch(long systemIdIn, long productIdIn, long subscriptionIdIn, int centGroupIdIn, int groupIdIn) {
        systemId = systemIdIn;
        productId = productIdIn;
        subscriptionId = subscriptionIdIn;
        centGroupId = centGroupIdIn;
        groupId = groupIdIn;
    }

    /**
     * Gets the system id.
     *
     * @return the system id
     */
    public long getSystemId() {
        return systemId;
    }

    /**
     * Gets the product id.
     *
     * @return the product id
     */
    public long getProductId() {
        return productId;
    }

    /**
     * Gets the subscription id.
     *
     * @return the subscription id
     */
    public long getSubscriptionId() {
        return subscriptionId;
    }

    /**
     * Gets the id of the cent group used by this match.
     *
     * @return the centGroupId
     */
    public int getCentGroupId() {
        return centGroupId;
    }

    /**
     * Gets the group id.
     *
     * @return the group id
     */
    public int getGroupId() {
        return groupId;
    }

    /** {@inheritDoc} */
    @Override
    public int hashCode() {
        return new HashCodeBuilder()
            .append(systemId)
            .append(productId)
            .append(subscriptionId)
            .append(centGroupId)
            .append(groupId)
            .toHashCode();
    }

    /** {@inheritDoc} */
    @Override
    public boolean equals(Object objIn) {
        if (!(objIn instanceof PartialMatch)) {
            return false;
        }
        PartialMatch other = (PartialMatch) objIn;
        return new EqualsBuilder()
            .append(systemId, other.systemId)
            .append(productId, other.productId)
            .append(subscriptionId, other.subscriptionId)
            .append(centGroupId, other.centGroupId)
            .append(groupId, other.groupId)
            .isEquals();
    }

    /** {@inheritDoc} */
    @Override
    public String toString() {
        return new ToStringBuilder(this, ToStringStyle.SHORT_PREFIX_STYLE)
            .append("systemId", systemId)
            .append("productId", productId)
            .append("subscriptionId", subscriptionId)
            .append("centGroupId", centGroupId)
            .append("groupId", groupId)
            .toString();
    }

    /** {@inheritDoc} */
    @Override
    public int compareTo(PartialMatch other) {
        return new CompareToBuilder()
            .append(systemId, other.systemId)
            .append(productId, other.productId)
            .append(subscriptionId, other.subscriptionId)
            .append(centGroupId, other.centGroupId)
            .append(groupId, other.groupId)
            .toComparison();
    }
}
