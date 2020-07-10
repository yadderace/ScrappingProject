CREATE TABLE public.encabezadoregistros
(
    codigoencabezado bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    idregistro bigint NOT NULL,
    linkpagina character varying(500) COLLATE pg_catalog."default" NOT NULL,
    fecharegistro date NOT NULL DEFAULT now(),
    registrolimpio bool NOT NULL DEFAULT false,
    fechalimpieza timestamp without time zone,
    CONSTRAINT encabezadoregistros_pkey PRIMARY KEY (codigoencabezado)
)
    

CREATE TABLE public.detalleregistros
(
    codigodetalle bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    codigoencabezado bigint NOT NULL,
    nombrecampo character varying(100) COLLATE pg_catalog."default" NOT NULL,
    valorcampo character varying(100) COLLATE pg_catalog."default",
    valorjson json,
    fecharegistro date NOT NULL DEFAULT now(),
	CONSTRAINT detalleregistros_codigoencabezado_fkey FOREIGN KEY (codigoencabezado)
        REFERENCES public.encabezadoregistros (codigoencabezado) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)


CREATE TABLE public.limpiezalog
(
    idlimpiezalog bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    cantidadregistros bigint NOT NULL,
    fechalimpieza timestamp without time zone DEFAULT now(),
    CONSTRAINT limpiezalog_pkey PRIMARY KEY (idlimpiezalog)
);


CREATE TABLE public.limpiezadetalle
(
    idlimpiezadetalle bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    idlimpiezalog bigint NOT NULL,
    nombrecampo character varying(50) NOT NULL,
	tipodatacampo character varying(50) NOT NULL,
	fecharegistro timestamp without time zone DEFAULT now(),
	CONSTRAINT limpiezadetalle_pkey PRIMARY KEY (idlimpiezalog, nombrecampo),
	CONSTRAINT limpiezadetalle_idlimpiezalog_fkey FOREIGN KEY (idlimpiezalog)
        REFERENCES public.limpiezalog(idlimpiezalog) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);


CREATE TABLE public.limpiezadata
(
    idlimpiezadata bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
	nombrecampo character varying (50) NOT NULL,
	idlimpiezalog bigint NOT NULL,
    valordata character varying (50) NOT NULL,
	fecharegistro timestamp without time zone DEFAULT now(),
	CONSTRAINT limpiezadata_pkey PRIMARY KEY (idlimpiezadata),
	CONSTRAINT limpiezadata_idlimpiezadetalle_fkey FOREIGN KEY (idlimpiezalog, nombrecampo)
        REFERENCES public.limpiezadetalle (idlimpiezalog, nombrecampo) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);


