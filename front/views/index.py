def index(env, data):
    m = env.models
    face_news = env.db.query(m.FaceNews).one()
    main_ids = [x.id for x in face_news.docs[:3]]
    main_news = face_news.docs[0]
    first_news = face_news.docs[1:3]

    query = env.db.query(m.MainDoc)\
                  .filter(~m.Doc.id.in_(main_ids))
    earlier_news =  query[:6]
    return env.render_to_response('index', dict(
            main_news=main_news,
            first_news=first_news,
            earlier_news=earlier_news,
        ))

