use strict;
use warnings;
use 5.010;

use Net::HTTP::API::Spec;

my $api = Net::HTTP::API::Spec->load_from_spec(shift);
my $res = $api->user_information(format => 'json', username => 'franckcuny');

use YAML::Syck; warn Dump $res;
