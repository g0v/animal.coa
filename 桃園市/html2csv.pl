use 5.12.0;
use utf8;
my (%l, %r);

use Text::CSV;
my $csv = Text::CSV->new ( { binary => 1, eol => $/ });
my $col_names = [ qw( 來源地點 入園日期 品種 備註 性別 收容原因 晶片號碼 毛色 體型 ) ];

my $file_in = shift or die $!;
my $file_out = $file_in;
$file_out =~ s/\.html$/.csv/ or die $file_out;

open my $fh, '>:utf8', $file_out or die $!;
$csv->print($fh, $col_names);
sub pp {
    my %in = @_;
    $csv->print( $fh, [ map { $in{$_} } @$col_names ] );
}
END { close $fh; }

open my $fh_in, '<:utf8', $file_in or die $!;
while (<$fh_in>) {
    next if 1 .. do { /(入園日期)：([^<>]+)/ and $l{$1} = $2 };
    next unless /([^<>]+)：([^<>]*)/;
    if (exists $l{$1}) {
        if (exists $r{$1}) {
            pp(%l);
            pp(%r);
            %l = %r = ();
            $l{$1} = $2;
        }
        else {
            $r{$1} = $2 // '';
        }
    }
    else {
        $l{$1} = $2 // '';
    }
}
