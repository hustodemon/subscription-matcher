#!/usr/bin/env ruby
# encoding: UTF-8

require 'rest-client'
require 'json'
require 'base64'

# Downloads a subscription data JSON file from SCC

if ARGV.length != 3
  puts "Usage: ./download-scc-subscriptions.rb ORG_NAME LOGIN PASSWORD"  
end

AUTH_HEADER = { :Authorization => 'Basic ' + Base64.encode64("#{ARGV[1]}:#{ARGV[2]}").chomp }

def process_rels(response)
  links = ( response.headers[:link] || '' ).split(', ').map do |link|
    href, name = link.match(/<(.*?)>; rel="(\w+)"/).captures

    [name.to_sym, href]
  end

  Hash[*links.flatten]
end

resp = RestClient.get('https://scc.suse.com/connect/organizations/subscriptions', AUTH_HEADER)
raise StandardError, "not successful response of #{resp.code}" unless resp.code == 200

subscriptions = []
loop do
 links = process_rels(resp)
 subscriptions += JSON.parse(resp)
 break unless links[:next]
 resp = RestClient.get(links[:next], AUTH_HEADER)
end

Dir.mkdir(ARGV[0])
File.open("#{ARGV[0]}/#{ARGV[1]}-subscriptions.json", 'w') { |file| file.write(JSON.pretty_generate(subscriptions)) }
