#!/usr/bin/perl

use strict;
use warnings;
use Data::Dumper;
use VMware::VIRuntime;

#Opts::add_options(
#       env_ip => {
#               type => "=s",
#               required => 1,
#               help => "Source Folder Name",
#       },
#);
Opts::parse();
Opts::validate();
Util::connect();

#my $env_ip = Opts::get_option('env_ip');
my $priority = "high";
my %priorityConstants = ('high' => 'highPriority', 'low' => 'lowPriority');
my $dest_regex = "";
my $env_ip = shift;
my $vm_array = Vim::find_entity_views( view_type => 'VirtualMachine',
        filter => { 'guest.ipAddress' => qr/$env_ip/ },
        properties => [ 'name', 'summary', 'datastore'] );

unless ( $vm_array ) {
        die "No vms found.\n";
}

foreach ( @$vm_array ) {
  my $ds_array = $_->datastore;
  my $ds = Vim::get_view( mo_ref => @$ds_array[0] );
#  print Dumper($ds);
  if ( ! ( $ds->summary->name =~ m/$dest_regex/ ) ) {
    print $_->name . "\n";
    my $ds = &cluster_drs_calc($_);
    &migrate_machine($_,$ds);
  }
}


sub cluster_drs_calc {

  # Get VM provided and all datastores in regex-matching cluster
  my $vm = shift;
  my $ds_array = Vim::find_entity_views( view_type => 'Datastore',
        filter => { 'name' => qr/$dest_regex/ },
        properties => [ 'summary' ] );
  # setting up vars to hold datastore info
  my $ds_reserved;
  my $last_free = 0;
  # Loop through all datastores in cluster, selecting subset
  # of ds which can hold VM, and also selecting the largest
  # free space within subset
  foreach ( @$ds_array ) {
    if ( $_->summary->freeSpace > $last_free ) {
      $last_free = $_->summary->freeSpace;
      $ds_reserved = $_;
    }
  }
  print "Using ds ".$ds_reserved->summary->name."\n";
  return $ds_reserved;
}

sub migrate_machine {
  my $vm = shift;
  my $datastore = shift;
  # relocate spec for both datastore, host
  my $spec = VirtualMachineRelocateSpec->new(datastore => $datastore->summary->datastore);
  my $migrationPriority = VirtualMachineMovePriority->new($priorityConstants{$priority});
  my ($task,$message);
  my $vmname = $vm->name;
  my $dsname = $datastore->summary->name;

#  print "$vmname $dsname\n";

  eval {
    # call relocate API
    print "Migrating:\t$vmname\tDatastore:\t$dsname \n";
    $task = $vm->RelocateVM_Task(spec => $spec, priority => $migrationPriority);
    $message = "Successfully migrated $vmname!\n";
    &get_status($task,$message);
  };

  if($@) {
    print "Error: " . $@ . "\n";
  }
}

sub get_status {
  my ($taskRef,$message) = @_;
  my $task_view = Vim::get_view(mo_ref => $taskRef);
  my $taskinfo = $task_view->info->state->val;
  my $continue = 1;
  while ($continue)
  {
    my $info = $task_view->info;
#    print $info->state->val."\n";
    if ($info->state->val eq 'success')
    {
      print $message,"\n";
      return $info->result;
      $continue = 0;
    }
    elsif ($info->state->val eq 'error')
    {
      my $soap_fault = SoapFault->new;
      $soap_fault->name($info->error->fault);
      $soap_fault->detail($info->error->fault);
      $soap_fault->fault_string($info->error->localizedMessage);
        die "$soap_fault\n";
    }
    sleep 5;
    $task_view->ViewBase::update_view_data();
  }
}

Util::disconnect();
exit;
