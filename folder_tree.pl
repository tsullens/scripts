#!/usr/bin/perl

use strict;
use warnings;
use VMware::VILib;
use VMware::VIRuntime;
use VMware::VIExt;

my %opts = (
        folder => {
        type => "=s",
        help => "Folder name",
        required => 0,
        },
);
Opts::add_options(%opts);
Opts::parse();
Opts::validate();
Util::connect();

my $folder = Opts::get_option('folder');
my $indent = 0;
my $datacenter_views;
if ( $folder ) {
  $datacenter_views = Vim::find_entity_views( view_type => 'Folder',
          filter => { 'name' => $folder },
          properties => [ 'name', 'childEntity' ] );
  foreach (@$datacenter_views) {
    if ( defined $_ ) {
      print "".$_->name."\n";
      traverse($_->childEntity, $indent);
    }
  }
}
else {
  $datacenter_views = Vim::find_entity_views( view_type => 'Datacenter',
          properties => [ 'name', 'vmFolder' ] );

foreach (@$datacenter_views) {
  if ( defined $_ ) {
    print "".$_->name."\n";
    print "".$_->vmFolder."\n";
#    traverse($_->vmFolder, $indent);
  }
}
}

sub traverse {
  my ( $ent_moref, $index ) = @_;
  my ( $num_entities, $ent_view, $child_view, $i, $mo );
  my ( $win_srvs, $lin_srvs, $unkn_srvs, $strg ) = (0,0,0,0);
  $index += 2;

  $ent_view = Vim::get_view( mo_ref => $ent_moref, properties => ['name', 'childEntity'] );
  $num_entities = defined( $ent_view->childEntity ) ? @{ $ent_view->childEntity } : 0;
  if ( $num_entities > 0) {
    foreach ( @{ $ent_view->childEntity } ) {
      $child_view = Vim::get_view( mo_ref => $_ );
      if ( $child_view->isa("VirtualMachine") ) {
#        print " " x $index . $child_view->name . "\n";
        my $os_info = ( defined ( $child_view->summary->guest->guestFullName ) ? $child_view->guest->guestFullName : "unknown");
        my $strg_arr  = ( defined ( $child_view->storage->perDatastoreUsage ) ? $child_view->storage->perDatastoreUsage : 0 );
#       print $os_info;
        if ( $os_info =~ m/Red Hat Enterprise Linux 6/ ) {
          $lin_srvs += 1;
        }
        elsif ( $os_info =~ m/Microsoft Windows Server 2008/ ) {
          $win_srvs += 1;
        }
        else {
          $unkn_srvs += 1;
        }
        foreach ( @{$strg_arr} ) {
          $strg += int ( $_->committed / 1024 / 1024 / 1024 );
        }
      }
      if ( $child_view->isa("Folder") ) {
        print " " x $index . "/" . $child_view->name . "\n";
        $child_view = Vim::get_view( mo_ref => $_, properties => ['name', 'childEntity'] );
        my @ret = &traverse($_, $index);
        $win_srvs += $ret[0];
        $lin_srvs += $ret[1];
        $unkn_srvs += $ret[2];
        $strg += $ret[3];
      }
    }
    print " " x $index . "Stats:\n" . " " x ($index + 2) . "Windows Srvs: " . $win_srvs . "\n" . " " x ($index + 2) . "Linux Srvs: " . $lin_srvs . "\n" . " " x ($index + 2) . "Unknown: " . $unkn_srvs . "\n" . " " x ($index + 2) . "Storage Used: " . $strg . "GB" . "\n";
  }
  return ( $win_srvs, $lin_srvs, $unkn_srvs, $strg );
}

Util::disconnect();
exit;
