<div id="alert-container">
% for message, css_class, dismissible, safe in status:
    <div class='alert alert-block alert-${css_class} fade in'>
        % if dismissible:
            <a class='close' data-dismiss='alert' href='#'>&times;</a>
        % endif
        % if safe:
            <p>${ message | n }</p>
        % else:
            <p>${ message }</p>
        % endif
    </div>
% endfor
</div>
