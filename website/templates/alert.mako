<script type="application/javascript">
    function capitaliseFirstLetter(string)
        {
            return string.charAt(0).toUpperCase() + string.slice(1);
        }
</script>
<div id="alert-container">
% for message, css_class, dismissible, safe in status:
        % if dismissible:
                <script type="application/javascript">
                    var title = capitaliseFirstLetter('${css_class | trim}')+':';
                    % if safe:
                        var message = '${message | n,trim }';
                    %else:
                        var message = '${message | trim}';
                    % endif
                    var type = '${css_class | trim}';
                    $.osf.growl(title, message, type);
                </script>
        % else:
            <div class='alert alert-block alert-${css_class} fade in'>
            % if safe:
                <p>${ message | n }</p>
            % else:
                <p>${ message }</p>
            % endif
            </div>
        % endif
% endfor
</div>
