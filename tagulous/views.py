from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

# ++ Can remove this try/except when min req is Django 1.5
try:
    import json
except ImportError:
   from django.utils import simplejson as json


@login_required
def autocomplete_login(*args, **kwargs):
    return autocomplete(*args, **kwargs)

def autocomplete(request, tag_model):
    """
    Arguments:
        request
            The request object from the dispatcher
        tag_model
            Reference to the tag model (eg myModel.tags.tag_model)
    
    The following GET parameters can be set:
        q   The query string to filter by
        p   The current page
            
    Response is a JSON object with following keys:
        results     List of tags
        more        Boolean if there is more
    }
    """
    # Get tag options
    options = tag_model.tag_options
    
    # Get query string
    query = request.GET.get('q', '')
    page = request.GET.get('p', 1)
    
    # Perform search
    if query:
        if options.force_lowercase:
            query = query.lower()
            
        if options.case_sensitive:
            results = tag_model.objects.filter(name__startswith=query)
        else:
            results = tag_model.objects.filter(name__istartswith=query)
    else:
        results = tag_model.objects.all()
    
    # Limit results
    if options.autocomplete_limit:
        start = options.autocomplete_limit * (page - 1)
        end = options.autocomplete_limit * page
        results = results.order_by('name')[start:end]
        more = results.order_by('name').count() > end
    
    # Build response
    response = {
        'results':  [tag.name for tag in results],
        'more':     more,
    }
    return HttpResponse(
        json.dumps(response, cls=DjangoJSONEncoder),
        mimetype='application/json',
    )
